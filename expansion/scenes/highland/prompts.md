# 高原与高山

## 生成顺序与来源

1. 内置 image_gen 生成效果图，保存 concept.png。
2. 内置 image_gen 生成地表贴图，保存 ground-texture.png。
3. Hyper3D Rodin 仅提交一次实际生成请求：e7a7f805-527e-42aa-896d-63b42ba012e4；当前 queued，模型由主 Agent 统一下载。

首次模型参数在生成前被长度校验拒绝（prompt > 1024），压缩到 941 字符后一次成功提交，无超时重试。

## 尺寸与检查

- concept.png：1672 × 941；PNG 签名有效；2,864,209 字节。效果图已目视检查，包含高耸雪山、裸岩深谷、发卡弯、挡墙、护栏和山口驿站。
- ground-texture.png：1254 × 1254；PNG 签名有效；2,870,499 字节。俯视砾石泥地纹理，按可平铺要求生成；接缝尚未技术验证。
- 风格参照：art-source/branding/avatar.png，明快卡通 3D、暖色高光、清晰形体。
- 模型参数：geometry_file_format=glb，mesh_mode=Raw，quality_override=18000，tier=Gen-2.5-Medium。

## 效果图提示词

Use case: stylized-concept. Asset type: wide 16:9 environment concept art for an original cheerful cartoon 3D mobile kart racing game, target 1536x864. Primary request: high plateau and towering alpine peaks race scene. A huge snow-capped mountain range rises vertically above a deep rocky gorge, tawny bare-rock high plateau terraces and layered craggy granite slopes. A very broad dark asphalt mountain race road snakes through two clear hairpin switchbacks at different heights, continuous rounded stone retaining walls and metal guardrails on the exposed road edges, red-white curb paint; safe wide track with readable road topology. One small stone mountain-pass roadside lodge with a warm terracotta roof sits on a road terrace, with a few sparse hardy shrubs. Composition: elevated cinematic three-quarter wide vista, foreground hairpin, middle-ground gorge and ascending road, tall distant snowy summits. Bright clear cyan sky, puffy white clouds, warm noon sun, soft shadows and clean material highlights. Style: colorful polished family-friendly cartoon 3D, rounded readable toy-like volumes, large coherent shapes, warm white highlights, high production quality, orange accents on barriers, cool blue shadowed mountains. Clearly a dramatic bare-rock high mountain environment, not rolling green grasslands. No vehicles or drivers required. No UI, letters, numbers, text, labels, logos, watermark. Full bleed single scene, no frames or collage.

## 地表贴图提示词

Use case: stylized-concept. Asset type: square seamless tileable highland gravel dirt ground albedo texture for a cheerful cartoon 3D mobile kart racing game, target 1024x1024. Primary request: uniform high-altitude bare-rock plateau ground, warm taupe clay soil and pale ochre fine grit dotted evenly with small smooth angular gray granite chips, very sparse muted ochre moss speckles. Orthographic directly overhead 90-degree top-down flat texture swatch only, fills image edge to edge, deliberately seamless in all four directions, repeated fine scale gravel pattern without a central feature. Hand-painted clean stylized game material, simplified shapes and restrained rounded details, readable at distance. Soft even neutral light, no directional shadows, no ambient occlusion, no highlights baked into material. No perspective, horizon, landscape, mountains, buildings, roads, tire tracks, foliage clumps, text, UI, labels, border, watermark. Medium-low contrast; pebble sizes mostly small, physically plausible gravel color, no black seams, no big rocks.

## 模型提示词

Cartoon 3D kart racing environment diorama: complete compact rocky highland mountain terrain tile with dramatic vertical height. Tawny bare granite terraces cut by a deep gorge; three tall gray peaks with white snowcaps at rear. Broad dark asphalt road climbs in two clear hairpin switchbacks across terrace levels. Continuous rounded stone retaining walls and orange-post metal guardrails protect exposed edges; red-white curbs. Small stone mountain-pass lodge with orange roof on upper terrace. Sparse hardy shrubs, mainly bare rock, no grassland. Clean toy-like rounded geometry, large readable shapes, colorful materials, warm ochre rock and cool gray-blue palette. Solid flat-bottom terrain base, all features attached, isolated self-contained asset viewable from every side. Road sits firmly on terraces, no floating parts. No cars, people, text, logos, UI, sky planes or billboards. Static low-poly art prototype, not a physics track.

## 静态原型限制

模型是完整小型环境地块美术原型，不是可直接使用的赛道碰撞网格。仍需后续拆分地形、道路、护栏、建筑，校准米制尺度与坐标轴，优化拓扑、材质和移动端预算，验证 Cocos 导入。赛车碰撞应继续使用已有 TrackBarriers.ts 体系。效果图不承诺模型精确复现；生成器实际面数需下载后核验。没有接入运行时或首包。贴图是单张基础色素材，不是完整 PBR 材质套。


## 图生模型修正

原生成 e7a7f805-527e-42aa-896d-63b42ba012e4 下载预览呈普通棕色小山弯道，缺少清晰高耸雪峰与山口驿站，未通过视觉验收。原 model.glb / preview.png 归档为 rejected.glb / rejected.png，移除旧 render-check.json。

保留 concept.png 和 ground-texture.png。内置 image_gen 以原效果图为风格参考生成 asset-reference.png（1254 × 1254，2,438,738 字节，PNG 签名有效）。目视检查确认主雪峰、两侧雪峰、开放盘山路和橙瓦石质小驿站均在完整地块内。

参考图通过 Hyper3D create_uploads + HTTP PUT 上传，HTTP 200，随后使用 reference_upload_ids 发起唯一一次新模型任务 4e6ee855-ac1e-47c0-9d46-a08d9f9ba30e。参数：glb / Raw / 18000 / Gen-2.5-Medium。当前 queued，主 Agent 下载后再次验收。没有等待或重复提交。

### 参考图提示词

Use case: stylized-concept. Create a new square 3D modeling reference image for a complete isolated original cartoon highland kart race diorama. Use the attached concept ONLY as style and theme reference; transform it into a single fully visible compact object on a plain light-gray studio background. Subject: a thin flat-bottom irregular gray rock terrain tile, at the REAR one very tall unmistakable white snow-covered main mountain peak and two smaller snow-capped side peaks, thick sculpted brilliant white snow occupying the upper half of every peak, gray exposed rock below. Main peak much taller than the entire lodge and road levels; bold alpine silhouette. FRONT and middle: gray-rock plateau terraces with a single broad open asphalt mountain hairpin road, stone retaining walls and continuous simple guardrails, red-white curbs. One clearly visible small stone mountain-pass lodge with bright orange terracotta roof on the front right terrace, separated from road. A few tiny tough shrubs, no green forest. Camera 45-degree overhead three-quarter orthographic product view; show entire diorama including all peaks, thin base and all edges with generous empty margin. Rounded clean colorful cartoon 3D material, large simplified game-ready shapes and soft studio lighting, clear vertical height difference. Strong cold gray/white mountain colors with warm orange lodge accent. No cars, no people, no text, no labels, no watermarks. No horizon, sky, distant painted scenery, cropped peaks or thick pedestal. All mountains must be actual connected 3D forms on the tile, and road surface open and clear.

### 图生模型提示词

Faithfully reconstruct the entire reference diorama as a textured 3D asset. Preserve the very tall white snow-covered rear main peak and two smaller snowy side peaks, gray exposed rock, broad open dark asphalt mountain hairpins with stone retaining walls and continuous guardrails, red-white curbs, and clearly visible orange-roof stone mountain-pass lodge on front-right terrace. Preserve strong vertical mountain height, all peaks fully modeled in geometry and snow visibly white. Single connected thin-base rocky terrain tile, no thick pedestal, no background plane. Original bright rounded cartoon 3D style. Keep road surface unobstructed and broad. No cars, people, text, trees, billboards, extra buildings. All mountain peaks and lodge must remain recognizable and distinct. Match reference colors and layout. Complete object visible from all sides.
