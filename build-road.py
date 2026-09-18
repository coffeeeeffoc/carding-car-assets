"""Rebuild precisely sized road props using only Python's standard library."""
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build(name, pieces, texture=False):
    groups = {}
    for material, polygon, start, end in pieces:
        vertices, normals, uvs, indices = groups.setdefault(material, ([], [], [], []))

        def face(points):
            a, b, c = points[:3]
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - a[i] for i in range(3)]
            n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            size = math.sqrt(sum(x*x for x in n))
            assert size > 0
            n = [x/size for x in n]
            offset = len(vertices)//3
            for x, y, z in points:
                vertices.extend((x, y, z))
                normals.extend(n)
                uvs.extend((x/2, z/2) if abs(n[1]) > .9 else ((x+y)/2, z/2))
            for i in range(1, len(points)-1):
                indices.extend((offset, offset+i, offset+i+1))

        for i, a in enumerate(polygon):
            b = polygon[(i+1) % len(polygon)]
            face([(*a, start), (*b, start), (*b, end), (*a, end)])
        face([(*p, end) for p in polygon])
        face([(*p, start) for p in reversed(polygon)])

    data = bytearray()
    views, accessors = [], []

    def blob(payload, target=None):
        data.extend(b'\0' * (-len(data) % 4))
        view = {'buffer': 0, 'byteOffset': len(data), 'byteLength': len(payload)}
        if target:
            view['target'] = target
        views.append(view)
        data.extend(payload)
        return len(views)-1

    def accessor(values, components, integer=False):
        view = blob(struct.pack('<' + ('I' if integer else 'f')*len(values), *values), 34963 if integer else 34962)
        a = {'bufferView': view, 'componentType': 5125 if integer else 5126,
             'count': len(values)//components, 'type': {1:'SCALAR', 2:'VEC2', 3:'VEC3'}[components]}
        if components == 3:
            a.update(min=[min(values[i::3]) for i in range(3)], max=[max(values[i::3]) for i in range(3)])
        accessors.append(a)
        return len(accessors)-1

    colors = [(1,1,1,1), (.91,.16,.10,1), (.95,.88,.70,1)]
    materials = [{'name': n, 'pbrMetallicRoughness': {'baseColorFactor': colors[i], 'metallicFactor': 0, 'roughnessFactor': .94 if i == 0 else .72}}
                 for i, n in enumerate(['asphalt', 'coral', 'ivory'])]
    doc = {'asset': {'version':'2.0', 'generator':'carding-car road kit / stdlib'}, 'scene':0,
           'scenes':[{'nodes':[0]}], 'nodes':[{'name':name, 'mesh':0}], 'meshes':[{'primitives':[]}],
           'materials':materials, 'bufferViews':views, 'accessors':accessors}
    if texture:
        doc['images'] = [{'bufferView':blob((ROOT/'asphalt-basecolor.png').read_bytes()), 'mimeType':'image/png'}]
        doc['samplers'] = [{'magFilter':9729, 'minFilter':9987, 'wrapS':10497, 'wrapT':10497}]
        doc['textures'] = [{'source':0, 'sampler':0}]
        materials[0]['pbrMetallicRoughness']['baseColorTexture'] = {'index':0}
    for material, (vertices, normals, uvs, indices) in groups.items():
        doc['meshes'][0]['primitives'].append({'attributes':{'POSITION':accessor(vertices,3), 'NORMAL':accessor(normals,3), 'TEXCOORD_0':accessor(uvs,2)}, 'indices':accessor(indices,1,True), 'material':material})
    doc['buffers'] = [{'byteLength':len(data)}]
    data.extend(b'\0' * (-len(data) % 4))
    header = json.dumps(doc, separators=(',',':')).encode()
    header += b' ' * (-len(header) % 4)
    result = struct.pack('<III', 0x46546C67, 2, 28+len(header)+len(data)) + struct.pack('<II',len(header),0x4E4F534A) + header + struct.pack('<II',len(data),0x004E4942) + data
    destination = ROOT/'road'/f'{name}.glb'
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(result)


def profile(x, width, bottom, top, bevel=0):
    a, b = x-width/2, x+width/2
    if bevel:
        return [(a,bottom),(b,bottom),(b,top-bevel),(b-bevel,top),(a+bevel,top),(a,top-bevel)]
    return [(a,bottom),(b,bottom),(b,top),(a,top)]


if __name__ == '__main__':
    road = [(0,profile(0,14,-.16,0),-4,4)]
    road += [(2,profile(x,.14,.001,.006),-4,4) for x in [-6.75,6.75]]
    for x in [-7.3,7.3]:
        road += [(1+i%2,profile(x,.6,0,.14,.05),-4+i*2,-2+i*2) for i in range(4)]
    build('road-straight-14x8', road, texture=True)
    build('kerb-4m', [(1+i%2,profile(0,.6,0,.14,.05),-2+i*2,i*2) for i in range(2)])
    build('barrier-4m', [(1+i%2,profile(0,.6,0,.75,.09),-2+i*2,i*2) for i in range(2)])
    print('Built road, kerb and barrier: Y up, metres, Z along road.')
