"""Build the three reusable highland props; source art and shared manifest stay untouched.

python build-highland-props.py [--check]
"""
import hashlib
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('expansion', ROOT / 'build-expansion.py')
expansion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expansion)
Model = expansion.Model
OUT = ROOT / 'runtime-expansion' / 'props'
KIT = ROOT / 'theme-kits' / 'highland'
SOURCE = ROOT / 'expansion' / 'scenes' / 'highland' / 'model.glb'


def snow_ridge():
    """Clip the authored upper mountains, interpolating UVs at the cut; no source road remains."""
    doc, data = expansion.read_glb(SOURCE)
    primitive = doc['meshes'][0]['primitives'][0]
    points = expansion.attribute(doc, data, primitive['attributes']['POSITION'])[0]
    uv = expansion.attribute(doc, data, primitive['attributes']['TEXCOORD_0'])[0]
    indices = [v[0] for v in expansion.attribute(doc, data, primitive['indices'])[0]]
    cutoff = -0.015
    clipped, faces, texcoords = [], [], []
    for i in range(0, len(indices), 3):
        polygon = [list(points[j]) + list(uv[j]) for j in indices[i:i + 3]]
        result = []
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            inside_a, inside_b = a[1] >= cutoff, b[1] >= cutoff
            if inside_a:
                result.append(a)
            if inside_a != inside_b:
                t = (cutoff - a[1]) / (b[1] - a[1])
                result.append([a[k] + (b[k] - a[k]) * t for k in range(5)])
        if len(result) < 3:
            continue
        start = len(clipped)
        clipped.extend(v[:3] for v in result)
        texcoords.extend(v[3:] for v in result)
        for j in range(1, len(result) - 1):
            faces.extend((start, start + j, start + j + 1))
    # The horizontal cut can isolate tiny roof/vegetation tips. Keep only actual mountain components.
    parents = list(range(len(clipped)))
    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index
    positions = {}
    for i, p in enumerate(clipped):
        key = tuple(round(v, 5) for v in p)
        if key in positions:
            parents[root(i)] = root(positions[key])
        else:
            positions[key] = i
    for i in range(0, len(faces), 3):
        a, b, c = faces[i:i + 3]
        parents[root(b)] = parents[root(c)] = root(a)
    components = {}
    for i in range(0, len(faces), 3):
        components.setdefault(root(faces[i]), []).extend(faces[i:i + 3])
    faces = [j for component in components.values() if len(component) >= 300 for j in component]
    used = sorted(set(faces))
    remap = {old: new for new, old in enumerate(used)}
    clipped, texcoords = [clipped[i] for i in used], [texcoords[i] for i in used]
    faces = [remap[i] for i in faces]
    lo, hi = expansion.bounds(clipped)
    factor = 64 / max(hi[0] - lo[0], hi[2] - lo[2])
    center = [(lo[0] + hi[0]) / 2, cutoff, (lo[2] + hi[2]) / 2]
    clipped = [[(p[i] - center[i]) * factor for i in range(3)] for p in clipped]
    image_view = doc['bufferViews'][doc['images'][0]['bufferView']]
    image_start = image_view.get('byteOffset', 0)
    texture = expansion.jpg(data[image_start:image_start + image_view['byteLength']], 512)
    model = Model()
    model.mesh('AuthoredSnowRidge', clipped, faces, [1, 1, 1, 1], texcoords, texture)
    return model


def cliff():
    model = Model()
    # Shared rugged column module: irregular cross sections, slanted strata and tapered pinnacles.
    for column, (x, z, radius, height) in enumerate([(-4, 0, 3, 14), (0, -1, 3.9, 19), (4, .3, 2.8, 16)]):
        rings = [(0, 1.12), (.15, 1), (.46, .94), (.76, .72), (.94, .46), (1, .09)]
        sides = 9
        def point(ring, i):
            y, taper = rings[ring]
            angle = (i % sides) * math.tau / sides
            r = radius * taper * (1 + .15 * math.sin(i * 2.7 + column))
            return [x + math.cos(angle) * r + y * .8,
                    height * y * (1 + .05 * math.sin(i * 1.9 + column)),
                    z + math.sin(angle) * r * .78]
        for ring in range(len(rings) - 1):
            for i in range(sides):
                shade = .80 + .15 * max(0, math.cos(i * math.tau / sides + 1))
                color = [v * shade for v in (.66 + (ring % 2) * .06, .63 + (ring % 2) * .05, .55 + (ring % 2) * .05)] + [1]
                model.mesh('Granite', [point(ring, i), point(ring + 1, i), point(ring + 1, i + 1), point(ring, i + 1)], [0, 1, 2, 0, 2, 3], color)
        for i in range(sides):
            model.mesh('Peak', [point(len(rings) - 1, i), [x + .8, height, z], point(len(rings) - 1, i + 1)], [0, 1, 2], [.68, .65, .58, 1])
    return model


def lodge():
    model = Model()
    stone, dark, wood = [.67, .63, .53, 1], [.22, .18, .14, 1], [.42, .27, .15, 1]
    model.box('StonePlinth', (0, .5, 0), (15, 1, 12), [.51, .48, .40, 1])
    model.box('Walls', (0, 3.7, -1), (11, 5.4, 8), [.78, .72, .60, 1])
    # Large offset masonry courses stay legible at racing speed.
    for row in range(5):
        for i in range(8):
            x = -4.8 + i * 1.36 + (row % 2) * .20
            for z in [-5.025, 3.025]:
                model.box('StoneCourse', (x, 1.35 + row * .66, z), (1.23, .53, .10), stone if (i + row) % 3 else [.72, .68, .58, 1])
    for x in [-5.55, 5.55]:
        for z in [-4.7, -.9, 2.7]:
            model.box('TimberPost', (x, 3.6, z), (.24, 5.2, .24), wood)
    for y in [1.2, 4.2, 6.3]:
        model.box('FrontTimber', (0, y, 3.08), (11.4, .22, .20), wood)
    for z in [-5, 3]:
        model.mesh('Gable', [[-5.5, 6.4, z], [5.5, 6.4, z], [0, 9.6, z]], [0, 1, 2, 2, 1, 0], [.82, .77, .66, 1])
    for side in [-1, 1]:
        model.mesh('TerracottaRoof', [[0, 9.75, -5.9], [side * 6.4, 6.2, -5.9], [side * 6.4, 6.2, 4], [0, 9.75, 4]], [0, 1, 2, 0, 2, 3, 2, 1, 0, 3, 2, 0], [.72 if side < 0 else .88, .30 if side < 0 else .40, .15, 1])
        for row in range(1, 7):
            x, y = side * row * .88, 9.80 - row * .88 * 3.55 / 6.4
            model.box('RoofTileRow', (x, y, -.95), (.09, .09, 9.9), [.97, .49, .23, 1])
    model.box('RidgeTile', (0, 9.8, -.95), (.28, .26, 10), [.93, .44, .21, 1])
    model.box('Chimney', (-3.2, 8.8, -2.4), (1.1, 3.3, 1.1), stone)
    model.box('ChimneyCap', (-3.2, 10.5, -2.4), (1.4, .27, 1.4), [.48, .43, .35, 1])
    model.box('Door', (0, 2.6, 3.16), (1.7, 3.1, .18), dark)
    for x in [-3.5, 3.5]:
        model.box('WindowFrame', (x, 3.9, 3.19), (2.1, 2.1, .25), wood)
        model.box('WindowGlass', (x, 3.9, 3.35), (1.7, 1.7, .08), [.47, .72, .79, 1])
        model.box('WindowCross', (x, 3.9, 3.42), (.14, 1.8, .07), [.88, .79, .58, 1])
        model.box('WindowCross', (x, 3.9, 3.42), (1.8, .14, .07), [.88, .79, .58, 1])
    model.box('PorchDeck', (0, 1.17, 4.55), (13, .3, 2.6), wood)
    for x in [-6, -3.5, 3.5, 6]:
        model.box('PorchPost', (x, 2.05, 5.65), (.22, 1.9, .22), wood)
    for side in [-1, 1]:
        for y in [1.9, 2.8]:
            model.box('PorchRail', (side * 3.8, y, 5.65), (4.6, .17, .17), wood)
    for i in range(3):
        model.box('EntryStep', (0, .18 + i * .17, 6.6 - i * .42), (2.7, .36 + i * .34, .65), stone)
    return model


def write_prop(name, model, usage, source):
    path = OUT / (name + '.glb')
    if name != 'highland-snow-ridge':
        # One shared palette atlas keeps each repeated crag/lodge to one draw call.
        colors = list(dict.fromkeys(tuple(m['pbrMetallicRoughness']['baseColorFactor'][:3]) for m in model.doc['materials']))
        side = math.ceil(math.sqrt(len(colors)))
        atlas = expansion.Image.new('RGB', (side * 16, side * 16))
        for index, color in enumerate(colors):
            for y in range(index // side * 16, (index // side + 1) * 16):
                for x in range(index % side * 16, (index % side + 1) * 16):
                    atlas.putpixel((x, y), tuple(round(v * 255) for v in color))
        points, faces, uv = [], [], []
        for mesh in model.doc['meshes']:
            for primitive in mesh['primitives']:
                color = tuple(model.doc['materials'][primitive['material']]['pbrMetallicRoughness']['baseColorFactor'][:3])
                index = colors.index(color)
                vertices = expansion.attribute(model.doc, model.data, primitive['attributes']['POSITION'])[0]
                faces.extend(i[0] + len(points) for i in expansion.attribute(model.doc, model.data, primitive['indices'])[0])
                points.extend(vertices)
                uv.extend([((index % side + .5) / side, (index // side + .5) / side)] * len(vertices))
        texture = io.BytesIO()
        atlas.save(texture, 'JPEG', quality=100, subsampling=0)
        model = Model()
        model.mesh('Palette', points, faces, [1, 1, 1, 1], uv, texture.getvalue())
    expansion.save(model.doc, expansion.compressed(model.doc, model.data, 512), path)
    row = {'category': 'props', 'id': name, **expansion.digest(path), 'bounds': expansion.bounds(model.points), 'usage': usage, 'source': source}
    if source.endswith('.glb'):
        row['sourceSha256'] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    return row


def validate():
    rows = json.loads((KIT / 'manifest.json').read_text(encoding='utf-8'))['models']
    total = 0
    for row in rows:
        path = ROOT / 'runtime-expansion' / row['file']
        assert expansion.digest(path)['sha256'] == row['sha256']
        doc, data = expansion.read_glb(path)
        points, triangles = [], 0
        assert all('uri' not in v for v in doc.get('images', []) + doc['buffers'])
        for m in doc['meshes']:
            for p in m['primitives']:
                vertices = expansion.attribute(doc, data, p['attributes']['POSITION'])[0]
                indices = expansion.attribute(doc, data, p['indices'])[0]
                assert len(indices) % 3 == 0 and all(0 <= i[0] < len(vertices) for i in indices)
                assert all(math.isfinite(n) for v in vertices for n in v)
                points.extend(vertices)
                triangles += len(indices) // 3
        lo, hi = expansion.bounds(points)
        assert abs(lo[1]) < 1e-5
        assert all(abs(v - row['bounds'][side][axis]) < 1e-4 for side, p in enumerate([lo, hi]) for axis, v in enumerate(p))
        assert triangles > 100
        if 'sourceSha256' in row:
            assert hashlib.sha256((ROOT / row['source']).read_bytes()).hexdigest() == row['sourceSha256']
        total += row['bytes']
        print(f"PASS {row['id']}: {triangles} triangles, {row['bytes']} bytes, grounded embedded GLB")
    assert total < 600_000, total


def build():
    """Shared exporter entry point: build props/metadata and return manifest-compatible rows."""
    KIT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [
        write_prop('highland-snow-ridge', snow_ridge(), '64m authored snow ridge; backdrop, cut base hidden by granite foothills', 'expansion/scenes/highland/model.glb'),
        write_prop('highland-cliff', cliff(), '15m wide faceted gray granite crag; entirely outside the driving envelope', 'build-highland-props.py'),
        write_prop('highland-lodge', lodge(), '15m stone lodge with terracotta gable roof and timber porch; +Z entrance', 'build-highland-props.py'),
    ]
    (KIT / 'manifest.json').write_text(json.dumps({'units': 'metres', 'up': '+Y', 'models': rows}, indent=2) + '\n', encoding='utf-8')
    return rows


if __name__ == '__main__':
    if '--check' not in sys.argv:
        build()
    validate()
