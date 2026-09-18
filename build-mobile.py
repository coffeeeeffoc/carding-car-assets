"""Export reusable mobile assets. Python 3 + Pillow; no game engine required."""
import hashlib
import io
import json
import math
import struct
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'runtime'


def read_glb(path):
    raw = path.read_bytes()
    size = struct.unpack_from('<I',raw,12)[0]
    return json.loads(raw[20:20+size]), bytearray(raw[28+size:])


def attribute(doc,data,index):
    a = doc['accessors'][index]
    view = doc['bufferViews'][a['bufferView']]
    width = {'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']]
    fmt = '<'+{5123:'H',5125:'I',5126:'f'}[a['componentType']]*width
    stride = view.get('byteStride',struct.calcsize(fmt))
    start = view.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from(fmt,data,start+i*stride) for i in range(a['count'])], (fmt,start,stride)


def export_model(name, height, pixels):
    source = ROOT/name/'base_basic_shaded.glb'
    doc,data = read_glb(source)
    assert len(doc['meshes']) == len(doc['nodes']) == len(doc['images']) == 1
    assert not any(k in doc['nodes'][0] for k in ['matrix','translation','scale','rotation'])
    p = doc['meshes'][0]['primitives'][0]
    points,layout = attribute(doc,data,p['attributes']['POSITION'])
    low = [min(v[i] for v in points) for i in range(3)]
    high = [max(v[i] for v in points) for i in range(3)]
    scale = [height/(high[1]-low[1])]*3
    if name == 'kart':
        scale = [2.16/(high[0]-low[0]), 2.9/(high[2]-low[2]), 2.9/(high[2]-low[2])]
    if name == 'coastal-rocks':
        scale = [4/(high[0]-low[0])]*3
    center = [(low[0]+high[0])/2, low[1], (low[2]+high[2])/2]
    positions = [[(v[i]-center[i])*scale[i] for i in range(3)] for v in points]
    fmt,start,stride = layout
    for i,v in enumerate(positions):
        struct.pack_into(fmt,data,start+i*stride,*v)
    a = doc['accessors'][p['attributes']['POSITION']]
    a['min'] = [min(v[i] for v in positions) for i in range(3)]
    a['max'] = [max(v[i] for v in positions) for i in range(3)]
    normals,(fmt,start,stride) = attribute(doc,data,p['attributes']['NORMAL'])
    for i,v in enumerate(normals):
        n = [v[j]/scale[j] for j in range(3)]
        length = math.sqrt(sum(x*x for x in n)) or 1
        struct.pack_into(fmt,data,start+i*stride,*[x/length for x in n])
    image = doc['images'][0]
    view = doc['bufferViews'][image['bufferView']]
    image_start = view.get('byteOffset',0)
    # These shaded exports put their only image last; fail rather than truncate other data.
    assert all(v is view or v.get('byteOffset',0)+v['byteLength'] <= image_start for v in doc['bufferViews'])
    texture = Image.open(io.BytesIO(data[image_start:image_start+view['byteLength']])).convert('RGB')
    texture.thumbnail((pixels,pixels),Image.Resampling.LANCZOS)
    encoded = io.BytesIO()
    texture.save(encoded,format='JPEG',quality=88,optimize=True)
    data = data[:image_start]+encoded.getvalue()
    view['byteLength'] = len(encoded.getvalue())
    image['mimeType'] = 'image/jpeg'
    image['name'] = 'shaded'
    doc['buffers'][0]['byteLength'] = len(data)
    data += b'\0'*(-len(data)%4)
    doc['scenes'][0]['name'] = name
    doc.setdefault('extensionsUsed',[]).append('KHR_materials_unlit')
    for material in doc['materials']:
        texture_info = material.pop('emissiveTexture')
        material.pop('emissiveFactor',None)
        material['pbrMetallicRoughness'] = {'baseColorTexture':texture_info,'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':1}
        material.setdefault('extensions',{})['KHR_materials_unlit'] = {}
    header = json.dumps(doc,separators=(',',':')).encode()
    header += b' '*(-len(header)%4)
    raw = struct.pack('<III',0x46546C67,2,28+len(header)+len(data))+struct.pack('<II',len(header),0x4E4F534A)+header+struct.pack('<II',len(data),0x004E4942)+data
    (OUT/f'{name}.glb').write_bytes(raw)
    return {'file':f'{name}.glb','source':str(source.relative_to(ROOT)).replace('\\','/'), 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'texture':texture.size,'bounds':[a['min'],a['max']]}


def road_profiles():
    result = {}
    for name in ['barrier','kerb']:
        doc,data = read_glb(ROOT/'road'/f'{name}-4m.glb')
        result[name] = []
        for p in doc['meshes'][0]['primitives']:
            geometry = {'positions':[], 'normals':[], 'indices':[]}
            for key,index in [('positions',p['attributes']['POSITION']),('normals',p['attributes']['NORMAL']),('indices',p['indices'])]:
                geometry[key] = [round(x,6) for v in attribute(doc,data,index)[0] for x in v]
            result[name].append({'material':p['material'],**geometry})
    (OUT/'road-profiles.json').write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    models = [export_model(name,height,pixels) for name,height,pixels in [('kart',0,1024),('palm',8,512),('broadleaf',7,512),('lighthouse',24,1024),('coastal-rocks',0,512)]]
    texture = Image.open(ROOT/'asphalt-basecolor.png').convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
    texture.save(OUT/'asphalt.jpg',quality=90,optimize=True)
    road_profiles()
    (OUT/'manifest.json').write_text(json.dumps({'models':models},indent=2)+'\n',encoding='utf-8')
    for m in models:
        assert m['bounds'][0][1] == 0 and m['bytes'] < 1500000
        print(m['file'],m['bytes'],'bytes',m['texture'])
    assert sum(p.stat().st_size for p in OUT.iterdir()) < 5*1024*1024
    print('PASS: grounded models, kart 2.16m wide / 2.9m long, runtime pack under 5 MiB')
