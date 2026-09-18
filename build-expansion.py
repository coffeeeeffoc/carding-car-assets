"""Export the expansion runtime pack. Python + Pillow; originals are never changed.

Run: python build-expansion.py [--check]
"""
import hashlib
import importlib.util
import io
import json
import math
import struct
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'expansion'
OUT = ROOT / 'runtime-expansion'
spec = importlib.util.spec_from_file_location('mobile', ROOT / 'build-mobile.py')
mobile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mobile)
read_glb, attribute = mobile.read_glb, mobile.attribute


def save(doc, data, path):
    doc['scenes'][0]['name'] = path.stem
    doc['buffers'] = [{'byteLength': len(data)}]
    data = bytes(data) + b'\0' * (-len(data) % 4)
    header = json.dumps(doc, separators=(',', ':')).encode()
    header += b' ' * (-len(header) % 4)
    raw = struct.pack('<III', 0x46546C67, 2, 28 + len(header) + len(data))
    raw += struct.pack('<II', len(header), 0x4E4F534A) + header
    raw += struct.pack('<II', len(data), 0x004E4942) + data
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_bytes(raw)


def jpg(payload, pixels=512):
    image = Image.open(io.BytesIO(payload)).convert('RGB')
    image.thumbnail((pixels, pixels), Image.Resampling.LANCZOS)
    result = io.BytesIO()
    image.save(result, 'JPEG', quality=82, optimize=True)
    return result.getvalue()


def compressed(doc, data, pixels):
    """Repack every buffer view, so no original PNG remains in the binary chunk."""
    # All exports are unlit. Omit unused normals and repack live accessors/views,
    # saving ~4 MiB without dropping a single visible triangle or UV coordinate.
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            primitive['attributes'].pop('NORMAL', None)
    # Source flat-shading duplicated vertices per normal seam. Once unlit, weld
    # exact POSITION+UV tuples; image seams stay distinct and no geometry changes.
    original_accessors, original_views = doc['accessors'], doc['bufferViews']
    compact_data, compact_accessors, compact_views = bytearray(), [], []
    def blob(payload):
        compact_data.extend(b'\0' * (-len(compact_data) % 4))
        compact_views.append({'buffer':0,'byteOffset':len(compact_data),'byteLength':len(payload)})
        compact_data.extend(payload)
        return len(compact_views)-1
    def rows(values, template, integer=False):
        a = dict(template)
        flat = [v for row in values for v in row]
        a.pop('byteOffset',None)
        a['componentType'] = 5123 if integer else 5126
        a['bufferView'] = blob(struct.pack('<'+('H' if integer else 'f')*len(flat),*flat))
        a['count'] = len(values)
        if a['type'] == 'VEC3':
            a['min'],a['max'] = bounds(values)
        compact_accessors.append(a)
        return len(compact_accessors)-1
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            keys = list(p['attributes'])
            streams = [attribute(doc,data,p['attributes'][k])[0] for k in keys]
            ids = [v[0] for v in attribute(doc,data,p['indices'])[0]] if 'indices' in p else list(range(len(streams[0])))
            unique, mapping, indices = [], {}, []
            for old in ids:
                key = tuple(stream[old] for stream in streams)
                if key not in mapping:
                    mapping[key] = len(unique); unique.append(key)
                indices.append((mapping[key],))
            assert len(unique)<65536
            p['attributes'] = {key:rows([row[j] for row in unique],original_accessors[p['attributes'][key]]) for j,key in enumerate(keys)}
            p['indices'] = rows(indices,{'type':'SCALAR'},True)
    for image in doc.get('images',[]):
        view = original_views[image['bufferView']]
        offset = view.get('byteOffset',0)
        image['bufferView'] = blob(data[offset:offset+view['byteLength']])
    doc['accessors'],doc['bufferViews'],data = compact_accessors,compact_views,compact_data
    images = {x['bufferView']: x for x in doc.get('images', [])}
    result = bytearray()
    for i, view in enumerate(doc['bufferViews']):
        offset = view.get('byteOffset', 0)
        payload = data[offset:offset + view['byteLength']]
        if i in images:
            payload = jpg(payload, pixels)
            images[i]['mimeType'] = 'image/jpeg'
        result.extend(b'\0' * (-len(result) % 4))
        view.update(byteOffset=len(result), byteLength=len(payload))
        result.extend(payload)
    doc['extensionsUsed'] = list(dict.fromkeys(doc.get('extensionsUsed', []) + ['KHR_materials_unlit']))
    for m in doc.get('materials', []):
        pbr = m.setdefault('pbrMetallicRoughness', {})
        if 'emissiveTexture' in m:
            pbr['baseColorTexture'] = m.pop('emissiveTexture')
            pbr['baseColorFactor'] = [1,1,1,1]
            m.pop('emissiveFactor', None)
        pbr.update(metallicFactor=0, roughnessFactor=1)
        m.setdefault('extensions', {})['KHR_materials_unlit'] = {}
    return result


def bounds(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def digest(path):
    raw = path.read_bytes()
    return {'file': path.relative_to(OUT).as_posix(), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


class Model:
    """Small indexed, unlit mesh writer shared by seated bodies and roadside props."""
    def __init__(self):
        self.data = bytearray()
        self.doc = {'asset': {'version': '2.0', 'generator': 'carding-car runtime expansion'},
                    'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
                    'materials': [], 'accessors': [], 'bufferViews': [],
                    'extensionsUsed': ['KHR_materials_unlit']}
        self.points = []

    def blob(self, payload):
        self.data.extend(b'\0' * (-len(self.data) % 4))
        self.doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(self.data), 'byteLength': len(payload)})
        self.data.extend(payload)
        return len(self.doc['bufferViews']) - 1

    def accessor(self, rows, integer=False):
        width = len(rows[0])
        values = [v for row in rows for v in row]
        component = 5123 if integer and max(values) < 65536 else 5125 if integer else 5126
        fmt = {5123: 'H', 5125: 'I', 5126: 'f'}[component]
        a = {'bufferView': self.blob(struct.pack('<' + fmt * len(values), *values)),
             'componentType': component, 'count': len(rows), 'type': {1: 'SCALAR', 2: 'VEC2', 3: 'VEC3'}[width]}
        if width == 3:
            a['min'], a['max'] = bounds(rows)
        self.doc['accessors'].append(a)
        return len(self.doc['accessors']) - 1

    def mesh(self, name, points, indices, color, uv=None, texture=None):
        normals = [[0., 0., 0.] for _ in points]
        for j in range(0, len(indices), 3):
            ids = indices[j:j + 3]
            a, b, c = [points[k] for k in ids]
            u, v = [[p[i] - a[i] for i in range(3)] for p in (b, c)]
            n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            for k in ids:
                normals[k] = [normals[k][i] + n[i] for i in range(3)]
        normals = [[v / (math.sqrt(sum(t*t for t in n)) or 1) for v in n] for n in normals]
        pbr = {'baseColorFactor': color, 'metallicFactor': 0, 'roughnessFactor': 1}
        material = {'name': name, 'pbrMetallicRoughness': pbr, 'extensions': {'KHR_materials_unlit': {}}}
        attributes = {'POSITION': self.accessor(points), 'NORMAL': self.accessor(normals)}
        if texture:
            self.doc.setdefault('images', []).append({'bufferView': self.blob(texture), 'mimeType': 'image/jpeg'})
            self.doc.setdefault('textures', []).append({'source': len(self.doc['images']) - 1})
            pbr['baseColorTexture'] = {'index': len(self.doc['textures']) - 1}
            attributes['TEXCOORD_0'] = self.accessor(uv)
        primitive = {'attributes': attributes, 'indices': self.accessor([(i,) for i in indices], True), 'material': len(self.doc['materials'])}
        self.doc['materials'].append(material)
        self.doc['scenes'][0]['nodes'].append(len(self.doc['nodes']))
        self.doc['nodes'].append({'name': name, 'mesh': len(self.doc['meshes'])})
        self.doc['meshes'].append({'name': name, 'primitives': [primitive]})
        self.points.extend(points)

    def box(self, name, center, size, color):
        points = [[center[i] + signs[i] * size[i] / 2 for i in range(3)]
                  for signs in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.mesh(name, points, [0,2,1,0,3,2,4,5,6,4,6,7,0,1,5,0,5,4,3,7,6,3,6,2,0,4,7,0,7,3,1,2,6,1,6,5], color)

    def rounded(self, name, center, size, color):
        points, uv, indices = [], [], []
        for y in range(9):
            theta = y*math.pi/8
            for x in range(13):
                phi = x*math.tau/12
                n = [math.sin(theta)*math.cos(phi), math.cos(theta), math.sin(theta)*math.sin(phi)]
                points.append([center[i]+n[i]*size[i]/2 for i in range(3)])
                uv.append([x/12,y/8])
        for y in range(8):
            for x in range(12):
                a=y*13+x
                indices.extend((a,a+1,a+14,a,a+14,a+13))
        # Small baked diffuse gradient keeps rounded body parts readable with the game's unlit material.
        texture=Image.new('RGB',(64,32))
        for y in range(32):
            theta=y*math.pi/31
            for x in range(64):
                phi=x*math.tau/63
                shade=.70+.30*max(0,math.sin(theta)*math.cos(phi)*.35+math.cos(theta)*.75+math.sin(theta)*math.sin(phi)*.55)
                texture.putpixel((x,y),tuple(min(255,round(c*255*shade)) for c in color[:3]))
        buffer=io.BytesIO();texture.save(buffer,'JPEG',quality=88)
        self.mesh(name,points,indices,[1,1,1,1],uv,buffer.getvalue())

    def mound(self, name, x, z, rx, rz, rings, colors, sides=12):
        # Ring coordinates are (height, radius factor); vertices are duplicated per band for clean color strata.
        for band, ((y0,r0),(y1,r1)) in enumerate(zip(rings, rings[1:])):
            points = [[x + math.cos(t*math.tau/sides)*rx*r, y, z + math.sin(t*math.tau/sides)*rz*r]
                      for y,r in [(y0,r0),(y1,r1)] for t in range(sides)]
            indices = []
            for t in range(sides):
                n = (t+1) % sides
                indices.extend((t, sides+t, sides+n, t, sides+n, n))
            self.mesh(name + str(band), points, indices, colors[band % len(colors)])

    def write(self, path):
        if path.parent.name == 'props':
            # Repeated windows share one draw call per color, rather than one per window.
            groups = {}
            for mesh in self.doc['meshes']:
                for p in mesh['primitives']:
                    material = self.doc['materials'][p['material']]
                    key = json.dumps(material['pbrMetallicRoughness'],sort_keys=True)
                    positions = attribute(self.doc,self.data,p['attributes']['POSITION'])[0]
                    indices = [v[0] for v in attribute(self.doc,self.data,p['indices'])[0]]
                    target, faces, color = groups.setdefault(key,([],[],material['pbrMetallicRoughness']['baseColorFactor']))
                    faces.extend(i+len(target) for i in indices);target.extend(positions)
            merged = Model()
            for i,(vertices,faces,color) in enumerate(groups.values()):
                merged.mesh('Part'+str(i),vertices,faces,color)
            save(merged.doc,compressed(merged.doc,merged.data,128),path)
            return bounds(self.points)
        save(self.doc, compressed(self.doc,self.data,512), path)
        return bounds(self.points)


DRIVER_COLORS = {'aviator':(.1,.65,.64,1), 'champion':(.12,.13,.15,1), 'explorer':(.72,.51,.27,1),
                 'future-pilot':(.50,.17,.75,1), 'mechanic':(.1,.48,.86,1), 'polar-guide':(.86,.89,.95,1),
                 'ranger':(.24,.62,.18,1), 'rookie':(1,.40,.08,1), 'speedster':(.86,.09,.10,1), 'street-racer':(.94,.18,.56,1)}
ENCLOSED = {'electric':(.18,-.15,.75),'mini-pickup':(.40,.20,.85),'muscle':(.18,-.15,.75),
            'rally':(.40,-.15,.85),'snow-tracks':(.25,-.15,.9),'supercar':(.12,-.15,.65)}


def seated_driver(source, target, id):
    doc, data = read_glb(source)
    p = doc['meshes'][0]['primitives'][0]
    pos, _ = attribute(doc, data, p['attributes']['POSITION'])
    uv, _ = attribute(doc, data, p['attributes']['TEXCOORD_0'])
    indices = [v[0] for v in attribute(doc, data, p['indices'])[0]]
    lo, hi = bounds(pos)
    # Preserve the actual source head, visor and helmet artwork, remove the standing body.
    cut = lo[1] + (hi[1] - lo[1]) * .67
    triangles = [indices[i:i+3] for i in range(0, len(indices), 3)
                 if min(pos[j][1] for j in indices[i:i+3]) >= cut]
    used = sorted({j for face in triangles for j in face})
    remap = {old: new for new, old in enumerate(used)}
    scale = .40 / (hi[1] - cut)
    points = [[(pos[j][0]-(lo[0]+hi[0])/2)*scale, .66+(pos[j][1]-cut)*scale,
               (pos[j][2]-(lo[2]+hi[2])/2)*scale-.13] for j in used]
    model = Model()
    image = doc['images'][0]
    view = doc['bufferViews'][image['bufferView']]
    start = view.get('byteOffset', 0)
    model.mesh('Helmet', points, [remap[j] for t in triangles for j in t], [1,1,1,1],
               [uv[j] for j in used], jpg(data[start:start+view['byteLength']], 512))
    color = DRIVER_COLORS[id]
    dark, gloves = (.12,.14,.19,1), (.92,.92,.83,1)
    model.rounded('Torso', (0,.51,-.13), (.40,.42,.31), color)
    model.box('Belt', (0,.345,-.13), (.34,.07,.27), dark)
    for sign, side in [(-1,'Left'),(1,'Right')]:
        model.rounded(side+'Thigh', (sign*.1,.31,.09), (.19,.19,.47), color)
        model.rounded(side+'Shin', (sign*.1,.17,.29), (.18,.30,.18), color)
        model.rounded(side+'Boot', (sign*.1,.055,.36), (.21,.11,.31), dark)
        model.rounded(side+'UpperArm', (sign*.23,.48,-.07), (.17,.32,.18), color)
        model.rounded(side+'Forearm', (sign*.23,.38,.11), (.16,.16,.38), color)
        model.rounded(side+'Glove', (sign*.23,.40,.29), (.18,.18,.18), gloves)
    return model.write(target)


def export(entry):
    category, id = entry['category'], entry['id']
    source = SOURCE / entry['directory'] / 'model.glb'
    target = OUT / category / (id + '.glb')
    if category == 'drivers':
        box = seated_driver(source, target, id)
    else:
        doc, data = read_glb(source)
        all_points = []
        # The authored spring has translated nodes; bake each translation before normalizing.
        for node in doc['nodes']:
            if 'mesh' not in node:
                continue
            translation = node.pop('translation', [0,0,0])
            if 'matrix' in node:
                matrix = node.pop('matrix')
                assert matrix[:12] == [1,0,0,0,0,1,0,0,0,0,1,0]
                translation = matrix[12:15]
            assert 'rotation' not in node and 'scale' not in node
            for p in doc['meshes'][node['mesh']]['primitives']:
                points, (fmt,start,stride) = attribute(doc,data,p['attributes']['POSITION'])
                points = [[v[i]+translation[i] for i in range(3)] for v in points]
                for j,v in enumerate(points):
                    struct.pack_into(fmt,data,start+j*stride,*v)
                all_points.extend(points)
        lo, hi = bounds(all_points)
        size = [hi[i]-lo[i] for i in range(3)]
        scale = 36 / max(size[0],size[2]) if category == 'scenes' else min(2.16/size[0],2.9/size[2]) if category == 'vehicles' else 1.1/max(size)
        if category == 'items' and id in ['boost-pad','oil-slick','roadblock','spring-pad','watermelon-peel']:
            scale = {'boost-pad':2.6,'oil-slick':2.0,'roadblock':2.2,'spring-pad':1.7,'watermelon-peel':1.2}[id] / max(size[0],size[2])
        center = [(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2]
        transformed = []
        for mesh in doc['meshes']:
            for p in mesh['primitives']:
                points, (fmt,start,stride) = attribute(doc,data,p['attributes']['POSITION'])
                points = [[(v[i]-center[i])*scale for i in range(3)] for v in points]
                for j,v in enumerate(points):
                    struct.pack_into(fmt,data,start+j*stride,*v)
                a = doc['accessors'][p['attributes']['POSITION']]
                a['min'], a['max'] = bounds(points)
                transformed.extend(points)
        box = bounds(transformed)
        if category == 'vehicles' and id in ENCLOSED:
            # Source cabins are opaque. Cut a small visible cockpit in the derived
            # chassis rather than showing a driver sitting on the original roof.
            mount_y,mount_z,mount_scale = ENCLOSED[id]
            center_z = mount_z-.13*mount_scale
            for mesh in doc['meshes']:
                for p in mesh['primitives']:
                    points,_ = attribute(doc,data,p['attributes']['POSITION'])
                    faces, (fmt,start,stride) = attribute(doc,data,p['indices'])
                    kept = []
                    for j in range(0,len(faces),3):
                        ids = [v[0] for v in faces[j:j+3]]
                        center_face = [sum(points[k][axis] for k in ids)/3 for axis in range(3)]
                        x,y,z = center_face
                        if not (abs(x)<.39 and center_z-.35<z<center_z+.45 and y>box[1][1]*.52):
                            kept.extend(ids)
                    # Reuse the original view; shortening the accessor skips removed faces.
                    for j,index in enumerate(kept):
                        struct.pack_into(fmt,data,start+j*stride,index)
                    accessor = doc['accessors'][p['indices']]
                    accessor['count'] = len(kept)
                    accessor.pop('min',None);accessor.pop('max',None)
            for material in doc['materials']:
                material['doubleSided'] = True
        save(doc, compressed(doc,data,512 if category == 'scenes' else 384), target)
        final_doc,final_data = read_glb(target)
        box = bounds([v for mesh in final_doc['meshes'] for p in mesh['primitives']
                      for v in attribute(final_doc,final_data,p['attributes']['POSITION'])[0]])
    row = {'category':category,'id':id,'name':entry['name'], **digest(target), 'bounds':box,
           'source':source.relative_to(ROOT).as_posix(), 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'usage':{'scenes':'distant landmark only; no driving or collision surface', 'vehicles':'visual chassis; shared game collision envelope',
                    'drivers':'seated rigid parts, textured original helmet; no skeletal animation', 'items':'visual pickup or hazard; game owns effects'}[category]}
    if category == 'vehicles':
        row['forward'] = '+Z'
        row['driverMount'] = {'x':0,'y':.30,'z':-.25,'scale':1}
        row['enclosedCabin'] = id in ['electric','mini-pickup','muscle','rally','snow-tracks','supercar']
        if id in ENCLOSED:
            y,z,scale = ENCLOSED[id]
            row['driverMount'] = {'x':0,'y':y,'z':z,'scale':scale}
            row['cockpitAdaptation'] = 'roof opening cut in runtime mesh; original source preserved'
        if id == 'formula':
            row['driverMount'] = {'x':0,'y':.15,'z':-.25,'scale':.7}
    if category == 'drivers':
        row.update(forward='+Z', seatPivot=[0,.32,-.13], pose='seated-rigid-parts')
    return row


def props():
    result = []
    def finish(id, model, usage):
        path = OUT/'props'/(id+'.glb')
        box = model.write(path)
        result.append({'category':'props','id':id,**digest(path),'bounds':box,'usage':usage,'source':'build-expansion.py'})
    m = Model()
    m.box('Facade',(0,6,0),(5,12,5),(.25,.58,.78,1))
    m.box('Roof',(0,12.2,0),(5.4,.4,5.4),(.13,.26,.39,1))
    for y in [2,4.3,6.6,8.9,11]:
        for x in [-1.5,0,1.5]:
            m.box('Window',(x,y,2.51),(.9,1.3,.05),(1,.90,.58,1))
            m.box('WindowRear',(x,y,-2.51),(.9,1.3,.05),(.65,.87,.94,1))
    finish('city-building',m,'5m wide building; outside barriers')
    m = Model()
    m.mound('Mountain',0,0,9,7,[(0,1),(8,.55),(12,.3),(17,0)],[(.43,.48,.54,1),(.7,.75,.8,1),(.97,.98,1,1)])
    finish('snow-peak',m,'18m wide snow peak; background')
    m = Model()
    for x in [-7,7]:
        m.box('Pillar',(x,4,0),(2,8,2.4),(.42,.8,.95,1))
    m.box('Lintel',(0,8.5,0),(16,1.5,2.4),(.71,.92,1,1))
    finish('ice-arch',m,'12m clear opening; roadside or wider game-defined opening, no collision')
    m = Model()
    m.mound('Strata',0,0,7,4.5,[(0,1),(1.6,.95),(3.2,.88),(4.8,.78),(6.4,.69),(8,.47),(9,.1)],
            [(.75,.25,.15,1),(.95,.58,.21,1),(.93,.81,.47,1),(.65,.22,.32,1),(.93,.42,.19,1),(.98,.69,.35,1)])
    finish('danxia-rock',m,'14m wide layered mesa; outside track')
    m = Model()
    m.mound('Hill',0,0,7,5,[(0,1),(1.6,.9),(3.2,.55),(4,0)],[(.36,.58,.22,1),(.48,.69,.26,1),(.59,.77,.33,1)])
    finish('grass-hill',m,'14m wide low grassy hill; outside track')
    m = Model()
    for x in [-10,10]:
        m.box('TowerLeg',(x,13,0),(2,26,2.5),(.86,.31,.17,1))
    for y in [18,25]:
        m.box('CrossBeam',(0,y,0),(22,1.4,2.5),(.95,.49,.23,1))
    finish('bridge-tower',m,'18m clear opening; deck at origin, collision supplied by game')
    m = Model()
    m.box('Deck',(0,.35,0),(18,.7,16),(.62,.65,.69,1))
    for x in [-8.6,8.6]:
        m.box('Rail',(x,1.1,0),(.35,.8,16),(.93,.91,.76,1))
    finish('bridge-deck',m,'18m x 16m visual deck; must align beneath authoritative road')
    m = Model()
    m.mound('Sandstone',0,0,5,4,[(0,1),(2,.91),(5,.72),(7,.28),(7.5,0)],[(.69,.37,.18,1),(.89,.60,.31,1),(.95,.73,.43,1),(.98,.82,.54,1)])
    finish('desert-rock',m,'10m wide sandstone formation; outside track')
    return result


def validate():
    manifest = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    rows = manifest['models']
    assert {c:sum(r['category']==c for r in rows) for c in ['scenes','vehicles','drivers','items','props']} == {'scenes':7,'vehicles':10,'drivers':10,'items':12,'props':8}
    for row in rows:
        path = OUT / row['file']
        assert digest(path)['sha256'] == row['sha256']
        doc, data = read_glb(path)
        assert all('uri' not in r for r in doc.get('images', []) + doc['buffers'])
        points = []
        for mesh in doc['meshes']:
            for p in mesh['primitives']:
                vertices = attribute(doc,data,p['attributes']['POSITION'])[0]
                indices = attribute(doc,data,p['indices'])[0] if 'indices' in p else [(i,) for i in range(len(vertices))]
                assert len(indices) % 3 == 0 and all(0 <= i[0] < len(vertices) for i in indices)
                assert all(math.isfinite(v) for p in vertices for v in p)
                points.extend(vertices)
        lo, hi = bounds(points)
        assert abs(lo[1]) < 1e-5, row['file']
        assert all(abs(v-row['bounds'][side][axis]) < 1e-4 for side,point in enumerate([lo,hi]) for axis,v in enumerate(point))
        if row['category'] == 'vehicles':
            assert hi[0]-lo[0] <= 2.16001 and hi[2]-lo[2] <= 2.90001
        for image in doc.get('images',[]):
            view = doc['bufferViews'][image['bufferView']]
            start = view.get('byteOffset',0)
            decoded = Image.open(io.BytesIO(data[start:start+view['byteLength']]))
            assert decoded.format == 'JPEG' and max(decoded.size) <= 512
        if 'sourceSha256' in row:
            assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest() == row['sourceSha256']
    assert len(manifest['textures']) == 7
    for row in manifest['textures']:
        assert digest(OUT/row['file'])['sha256'] == row['sha256']
    total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    assert total < 12*1024*1024, total
    print(f'PASS: 39 derived assets + 8 props + 7 textures, grounded embedded GLBs, originals intact; {total / 1024**2:.2f} MiB')


if __name__ == '__main__':
    if '--check' not in sys.argv:
        OUT.mkdir(exist_ok=True)
        catalog = json.loads((SOURCE/'catalog.json').read_text(encoding='utf-8'))
        models = [export(entry) for entry in catalog]
        models += props()
        textures = []
        for entry in catalog:
            if entry['category'] != 'scenes':
                continue
            candidates = list((SOURCE/entry['directory']).glob('*-texture.png'))
            assert len(candidates) == 1
            path = OUT/'textures'/(entry['id']+'.jpg')
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(jpg(candidates[0].read_bytes(),512))
            textures.append({'id':entry['id'],**digest(path),'usage':'environment reference texture; road tiling must be checked in scene'})
        manifest = {'version':1,'units':'metres','up':'+Y','forward':'+Z','models':models,'textures':textures,
                    'limitations':['Original scene dioramas are background landmarks, not drivable roads.',
                                    'Vehicle wheels remain baked into chassis; drivers use rigid seated parts without a skeleton.',
                                    'Six opaque source cabins have small runtime roof openings; use each vehicle driverMount.']}
        (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    validate()
