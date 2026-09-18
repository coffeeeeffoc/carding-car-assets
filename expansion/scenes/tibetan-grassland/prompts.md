# 青藏高原草原与小山 · 生成记录

## 顺序与来源

1. 内置 image_gen：先生成 concept.png。
2. 内置 image_gen：再生成 grass-texture.png。
3. Hyper3D Rodin：单次提交 GLB 场景地块；质量 18000、Raw、Gen-2.5-Medium。

## 效果图提示词

Use case: stylized-concept. Asset type: environment concept art for an original mobile kart racing game. Create a wide 3D cartoon Qinghai-Tibet plateau GRASSLAND racing scene, visibly open and gentle, with low rounded rolling green hills, vast jade and lime short-grass meadows, a few smooth gray rocks, a clear turquoise creek, small distant dark shaggy yak herds and two small white pastoral canvas tents. A generous smooth dark asphalt kart racetrack winds in a readable S curve across the foreground and meadow; white edge lines, red-white rounded curbs, simple silver safety guardrails. Crisp high-altitude blue sky with fluffy rounded white clouds. Camera: elevated three-quarter gameplay establishing view, show the track scale and open horizons. Style: polished joyful cartoon 3D game art, rounded substantial forms, clean color blocks, warm white sun highlights, soft shadows, saturated yet natural color, detailed enough to guide modular game assets. Distinguish this from alpine mountain racing: only LOW small hills, no huge snow peaks, no steep cliffs, no deep canyon, no dense city, no jungle. Environment only, no prominent kart, no driver. No text, no UI, no logos, no watermark. Landscape composition.

## 草地纹理提示词

Use case: stylized-concept. Asset type: seamless tileable albedo / base color ground texture for an original cheerful cartoon 3D kart racing game, Qinghai-Tibet plateau grassland. Generate one square texture showing dense very short alpine grass and sparse small earthy patches, soft spring green and olive green colors with tiny desaturated straw accents, simple rounded stylized blades, low contrast at distance, natural fine-scale variation without large motifs. Strict perfectly top-down orthographic surface view, edge to edge grass and soil only, no camera perspective, no horizon, no objects, no rocks, no flowers, no road, no animals, no sky. Uniform neutral diffuse lighting, no directional shadows, no specular glare, no baked ambient occlusion. Seamless repeating surface, matching opposite edges, no visible border, no framing. Cartoon 3D game material appearance, clean and restrained texture, not photorealistic. No text or watermark.

## 3D 模型提示词

Original cheerful cartoon 3D kart racing environment diorama: a compact Qinghai-Tibet plateau grassland terrain tile, broad green short-grass meadows with three LOW rounded small hills, a wide smooth charcoal asphalt S bend with white edge lines, red-white curbs and simple silver guardrails. A narrow turquoise creek beside the road, several smooth gray rocks, one small white pastoral canvas tent, two tiny dark shaggy yak figures away from the road. Complete cohesive self-contained terrain chunk on a simple low earth base, viewed three-quarter isometric, readable chunky rounded shapes, clean vivid colors, matte stylized game materials, warm soft daylight. Keep the terrain mostly open and low, no large snowy peaks, no cliffs, no canyon, no trees, no city, no cars or drivers. No text, no logos, no UI. All scene elements modeled as 3D geometry, road surface smooth and unbroken. Mobile game art source, not photorealistic.

## 验证与边界

- PNG 文件头和尺寸验证通过：concept.png 为 1672 × 941；grass-texture.png 为 1254 × 1254。
- 已检查效果图具有开阔草原、小山、宽阔弯道、溪流、帐篷和牦牛，未出现巨大雪峰或深峡谷。
- 草地纹理为俯视短草土地表面，无道路、建筑、文字；实际无缝平铺效果需后续材质验证。
- 模型属于完整静态环境地块美术源，不等同于可驾驶地图；碰撞、拆件、拓扑和移动端预算未验证。
- 模型生成记录：2823cbe0-3c1b-4117-ab67-2c4e9cd64574，当前提交状态 queued；根 Agent 统一轮询下载。

## 2026-09-19 修正：由完整地块参考图生成模型

首次模型渲染仅有断开的灰色道路条，缺少草原地块、小山和帐篷，因此不验收。旧模型与预览保留为 rejected.glb 和 rejected.png；旧 generation ID 为 2823cbe0-3c1b-4117-ab67-2c4e9cd64574。

### 参考图生成提示词（内置 image_gen，concept.png 作风格参考）

Use case: stylized-concept. Asset type: a single clear 3D reconstruction reference image of a miniature racing terrain diorama. Use the supplied concept image ONLY as a color and style reference; replace its panoramic composition with one isolated compact solid terrain block fully in frame on a neutral light-gray studio background. Subject: complete Qinghai-Tibet plateau grassland terrain tile, thick solid earth base covered with bright green short grass, several low rounded green grassy hills, a small turquoise creek, exactly two white pastoral canvas tents, and a wide gray asphalt S-bend racing road running across the ground surface. The road must sit firmly on the ground, with clear white guardrails along the edges. Include one small wooden bridge across the creek and a few simple gray stones. Camera: 45-degree elevated three-quarter isometric view, entire block and all its sides visible, clear margin around the asset. Simple readable miniature cartoon 3D, chunky smooth forms, matte colors, soft studio light, detailed enough to reconstruct the landmass and tents. Terrain must be a filled-in solid continuous green landmass, no holes or hollow center; most of the image shows grassland terrain, not road. Preserve the calm open grassland identity. No giant snowy peaks, no alpine mountains, no cliffs, no scenery outside the block, no sky, no people, no vehicles, no yaks, no text, no labels, no UI, no watermark.

### 图生 3D 提示词

Reconstruct the entire solid miniature grassland terrain block in the reference image. Include the thick filled-in earth base, continuous vivid green grass surface, low rounded grassy hills, two white pastoral canvas tents, turquoise stream and small wooden bridge. Preserve the broad gray asphalt S-bend road physically resting on the terrain, white guardrails and red-white curbs. A cohesive complete diorama, full landmass and grass surface are essential; do not output isolated floating road strips. Clean stylized cartoon 3D, matte colorful materials. No background geometry, no snow peaks, no people, no vehicles, no text.

参考图为完整独立实心草原地块，包含低矮绿丘、两个白色帐篷、溪流、小木桥、灰色 S 弯和白色护栏。PNG 头验证通过，1672 × 941，共 2224478 字节。已通过 rodin_create_uploads + HTTP PUT（200）上传，upload ID 为 0f13bcec-8fae-437d-a9d4-b2fbc389bd83。仅提交一次新生成：02ed6c9d-ab3b-4c18-bfd2-0408059e8429；Raw / 18000 / Gen-2.5-Medium / glb，提交状态 queued。根 Agent 负责下载与渲染检查。
