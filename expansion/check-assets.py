"""Validate delivered source assets and rebuild the offline preview gallery.

Run from carding-car-assets: python expansion/check-assets.py --complete
"""
import argparse
import collections
import html
import hashlib
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parent


def inspect_glb(path):
    data = path.read_bytes()
    assert len(data) >= 28, f"Truncated GLB: {path}"
    assert struct.unpack_from('<III', data) == (0x46546C67, 2, len(data)), path
    offset, chunks = 12, []
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        assert size % 4 == 0 and offset + 8 + size <= len(data), path
        chunks.append((kind, data[offset + 8:offset + 8 + size]))
        offset += size + 8
    assert offset == len(data) and chunks[0][0] == 0x4E4F534A, path
    doc = json.loads(chunks[0][1])
    binary = next(chunk for kind, chunk in chunks if kind == 0x004E4942)
    assert doc.get('meshes') and doc.get('scenes'), path
    assert len(doc['buffers']) == 1 and 'uri' not in doc['buffers'][0], path
    assert doc['buffers'][0]['byteLength'] <= len(binary), path
    for view in doc.get('bufferViews', []):
        assert view.get('buffer', 0) == 0, path
        assert 0 <= view.get('byteOffset', 0) <= len(binary), path
        assert view.get('byteOffset', 0) + view['byteLength'] <= len(binary), path
    for image in doc.get('images', []):
        assert 'uri' not in image and 'bufferView' in image, path
    triangles = 0
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4, path
            accessor = primitive.get('indices', primitive['attributes']['POSITION'])
            count = doc['accessors'][accessor]['count']
            assert count > 0 and count % 3 == 0, path
            triangles += count // 3
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'meshes': len(doc['meshes']), 'triangles': triangles,
            'materials': len(doc.get('materials', [])), 'images': len(doc.get('images', [])),
            'skins': len(doc.get('skins', [])), 'animations': len(doc.get('animations', []))}


def inspect_png(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR', path
    width, height = struct.unpack_from('>II', data, 16)
    assert width > 0 and height > 0, path
    return {'width': width, 'height': height, 'bytes': len(data)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--complete', action='store_true')
    args = parser.parse_args()
    catalog = []
    for path in sorted(ROOT.glob('*/*/asset.json')):
        entry = json.loads(path.read_text(encoding='utf-8-sig'))
        folder = path.parent.relative_to(ROOT).as_posix()
        entry['directory'] = folder
        model = path.parent / 'model.glb'
        entry['validation'] = {}
        if model.exists():
            entry['validation']['model'] = inspect_glb(model)
            entry['status'] = 'validated-static-source'
        elif args.complete:
            raise AssertionError(f'Missing model: {model}')
        for image in path.parent.glob('*.png'):
            entry['validation'][image.name] = inspect_png(image)
        if args.complete:
            assert entry.get('visualReview') == 'accepted-static-source', path
            assert (path.parent / 'preview.png').exists(), path
            if entry['category'] == 'scenes':
                assert (path.parent / 'concept.png').exists(), path
                assert (path.parent / entry['texture']).exists(), path
        path.write_text(json.dumps({k: v for k, v in entry.items() if k != 'directory'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        catalog.append(entry)
    counts = collections.Counter(entry['category'] for entry in catalog)
    if args.complete:
        assert counts == {'scenes': 7, 'vehicles': 10, 'drivers': 10, 'items': 12}, counts
        assert len({(e['category'], e['id']) for e in catalog}) == 39
        assert len({e['validation']['model']['sha256'] for e in catalog}) == 39
    (ROOT / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {'scenes': '七个场景', 'vehicles': '十种车型', 'drivers': '十种车手', 'items': '十二种道具'}
    sections = []
    for category, title in groups.items():
        cards = []
        for entry in [e for e in catalog if e['category'] == category]:
            folder = entry['directory']
            image = 'concept.png' if category == 'scenes' else 'preview.png'
            preview = f'<a href="{folder}/{image}"><img loading="lazy" src="{folder}/{image}" alt="{html.escape(entry["name"])}"></a>' if (ROOT / folder / image).exists() else ''
            links = [f'<a href="{folder}/asset.json">生成记录</a>']
            for filename, label in [('model.glb', 'GLB'), ('preview.png', '模型实拍'), (entry.get('texture', ''), '贴图')]:
                if filename and (ROOT / folder / filename).is_file():
                    links.append(f'<a href="{folder}/{filename}">{label}</a>')
            if entry.get('displayUrl') and (ROOT / folder / 'model.glb').exists():
                links.append(f'<a href="{html.escape(entry["displayUrl"])}">在线旋转预览</a>')
            stats = entry['validation'].get('model', {})
            detail = f'{stats.get("triangles", "待生成")} 三角面 · {stats.get("bytes", 0) / 1048576:.1f} MB'
            cards.append(f'<article>{preview}<div><h3>{html.escape(entry["name"])}</h3><p>{detail}</p><nav>{" · ".join(links)}</nav></div></article>')
        sections.append(f'<section id="{category}"><h2>{title}</h2><div class="grid">{"".join(cards)}</div></section>')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>咔叮唓 · 扩展素材库</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f5f6;color:#163343;font-family:system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:32px}h1{font-size:36px;margin-bottom:8px}p{line-height:1.7}a{color:#067a83}header>nav{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}section{margin-top:44px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:20px}article{background:white;border-radius:16px;overflow:hidden;border:1px solid #dce6e9}img{display:block;width:100%;aspect-ratio:1;object-fit:contain;background:#edf3f6}#scenes .grid{grid-template-columns:repeat(auto-fill,minmax(340px,1fr))}#scenes img{aspect-ratio:16/9;object-fit:cover}article>div{padding:16px}h3{margin:0}article p{font-size:13px;color:#55717c}nav{font-size:14px;line-height:2}footer{margin-top:40px;font-size:14px;color:#55717c}@media(max-width:420px){main{padding:16px}#scenes .grid{grid-template-columns:1fr}h1{font-size:28px}}</style>
<main><header><h1>咔叮唓 · 扩展素材库</h1><p>7 个场景 · 10 种车型 · 10 种车手 · 12 种道具<br>场景首图为效果图；“模型实拍”为实际 GLB 渲染，可对照查看差异。</p><nav><a href="#scenes">场景</a><a href="#vehicles">车型</a><a href="#drivers">车手</a><a href="#items">道具</a></nav></header>'''
    page += ''.join(sections) + '<footer>静态美术源素材，尚未接入游戏。场景为整体地块原型，尚未拆出建筑和跑道模块；车手未绑定。碰撞、比例、贴图接缝与移动端优化在接入时处理。<br>生成工具：内置 image_gen + Hyper3D Rodin Gen-2.5；弹簧板按参考图用 Three.js 精确建模。完整提示词见各项生成记录和场景 prompts.md。</footer></main></html>'
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps({'counts': dict(counts), 'models': sum('model' in e['validation'] for e in catalog), 'bytes': sum(e['validation'].get('model', {}).get('bytes', 0) for e in catalog)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
