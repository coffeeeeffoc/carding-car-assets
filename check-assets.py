"""Validate standalone GLBs and record real counts; run with Python 3, no dependencies."""
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def inspect(path):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', raw)
    assert (magic, version, length) == (0x46546C67, 2, len(raw)), path
    json_size, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20+json_size])
    offset = 20+json_size
    binary_size, kind = struct.unpack_from('<II', raw, offset)
    assert kind == 0x004E4942 and offset+8+binary_size == len(raw)
    binary = raw[offset+8:]
    assert len(doc['buffers']) == 1 and 'uri' not in doc['buffers'][0]
    assert doc['buffers'][0]['byteLength'] <= binary_size
    for view in doc['bufferViews']:
        assert view['buffer'] == 0 and view.get('byteOffset',0)+view['byteLength'] <= binary_size

    def values(index):
        a = doc['accessors'][index]
        v = doc['bufferViews'][a['bufferView']]
        count = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4}[a['type']]
        fmt = '<'+{5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']]*count
        size = struct.calcsize(fmt)
        stride = v.get('byteStride',size)
        start = v.get('byteOffset',0)+a.get('byteOffset',0)
        assert a['count'] > 0 and stride >= size
        assert a.get('byteOffset',0)+(a['count']-1)*stride+size <= v['byteLength']
        return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a['count'])]

    triangles, points, primitives = 0, [], 0
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            assert p.get('mode',4) == 4
            positions = values(p['attributes']['POSITION'])
            assert all(math.isfinite(x) for row in positions for x in row)
            for attribute in ['NORMAL','TEXCOORD_0']:
                assert len(values(p['attributes'][attribute])) == len(positions)
            indices = values(p['indices'])
            assert len(indices)%3 == 0 and all(0 <= i[0] < len(positions) for i in indices)
            triangles += len(indices)//3
            points.extend(positions)
            primitives += 1
    images = []
    for im in doc.get('images',[]):
        assert 'uri' not in im and im['mimeType'] == 'image/png'
        v = doc['bufferViews'][im['bufferView']]
        png = binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
        images.append({'name':im.get('name','basecolor'), 'size':list(struct.unpack_from('>II',png,16))})
    bounds = [[min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]]
    return {'file':path.relative_to(ROOT).as_posix(), 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(), 'triangles':triangles, 'primitives':primitives, 'materials':len(doc['materials']), 'bounds':bounds, 'textures':images, 'animations':len(doc.get('animations',[]))}


if __name__ == '__main__':
    results = [inspect(p) for p in sorted(ROOT.rglob('*.glb')) if 'runtime' not in p.relative_to(ROOT).parts]
    assert len(results) == 13, 'Expected five PBR/shaded pairs plus three road modules'
    road = next(r for r in results if 'road-straight' in r['file'])
    assert abs(road['bounds'][1][2]-road['bounds'][0][2]-8) < .001
    assert abs(road['bounds'][1][0]-road['bounds'][0][0]-15.2) < .001
    for r in results:
        print(f"{r['file']}: {r['triangles']} triangles, {r['bytes']/1024/1024:.2f} MiB")
    (ROOT/'validation.json').write_text(json.dumps({'glbVersion':2, 'files':results},indent=2)+'\n',encoding='utf-8')
    print('PASS: structure, embedded textures, indices, finite geometry, UVs/normals, road dimensions.')
