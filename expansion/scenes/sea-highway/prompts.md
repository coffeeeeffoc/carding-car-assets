# 跨海高速素材生成记录

生成顺序：效果图 → 海水贴图 → Rodin 静态场景地块。

图片使用内置 `image_gen`，保留真实生成文件；视觉风格参考 `art-source/branding/avatar.png`。模型基于对应文字描述生成，没有上传效果图。

## 效果图

文件：`concept.png`，1536 × 1024。

Use case: stylized-concept. Asset type: original cartoon 3D kart racing game environment concept art, scene sea-highway. Create a beautiful wide landscape establishing view of a long white cable-stayed bridge racing highway over a bright azure sea. The broad asphalt racetrack visibly rises and dips gently over several spans, with safe continuous white barriers and red-white curb accents. Elegant clean white bridge towers and clearly readable supporting cables, sunny turquoise ocean under the bridge, distant small green rocky islands, a small white lighthouse with a red cap on one island. Camera: high three-quarter aerial view showing the whole bridge route diagonally across the scene, readable race track width and terrain structure, horizon and pleasant sky. Stylized polished cartoon 3D toy-like rendering, chunky rounded forms, clear vivid color blocks, warm-white highlights and soft ambient shadows, matching the cheerful aesthetic of an orange-and-white chibi kart game. Environment only, no cars or characters. Sunny clear blue sky with a few fluffy white clouds. No text, labels, logos, watermarks, UI, photorealism, or city skyline. Landscape composition, 1536x1024.

## 海水贴图

文件：`water-texture.png`，1254 × 1254（工具实际尺寸；提示词请求 1024 × 1024）。平铺目标已写入提示词，实际接缝仍需导入后验收。

Use case: stylized-concept. Asset type: seamless tileable sea-water color texture for a cheerful cartoon 3D kart racing game. Create one square perfectly top-down orthographic flat ocean-water texture covering the entire image edge to edge. Turquoise and azure blue water, simplified rounded flowing ripples and small pale cyan foam highlights, polished stylized 3D cartoon color treatment, clean readable medium-scale pattern, subtle brightness variation but no large dark-light gradient. No horizon, no perspective, no shore, no rocks, no islands, no bridge, no objects, no fish, no text, no frame, no logo, no watermark. Pattern should be continuous and visually matching on all opposite edges for horizontal and vertical tiling. Uniform soft neutral light with no directional shadows and no sun reflection hotspot. This is a diffuse/albedo texture asset, not a scene illustration. Square 1024x1024.

## 场景模型

目标文件：`model.glb`，静态环境地块；Raw / 18000 polygons / Gen-2.5-Medium。

Original cheerful cartoon 3D kart racing environment diorama: sea highway, a long white cable-stayed bridge with two strong white towers and visibly simplified thick cable stays, a broad dark gray asphalt racetrack gently rising and dipping over spans, continuous white guardrails and red-white curbs, supported over a thick turquoise blue sea-water base. Include two small rounded rocky green islands alongside the bridge and a small white lighthouse with red roof on one island. Whole self-contained single static scene tile with visible base, all structures connected to the diorama. Rounded chunky toy-like forms, saturated turquoise azure and white palette, warm-white highlights, simple clean materials, polished mobile cartoon game style. Bridge route clearly readable and wide. No cars, no people, no sky geometry, no text, no logos. Low polygon environment art prototype, not a physically validated playable track. Use stable readable silhouettes rather than very thin details.

生成任务 ID：`65588f8f-0a50-48d4-bb46-50ecbd751b25`。提交状态为 queued，主 Agent 统一跟进下载。未经碰撞、拓扑、Cocos 导入或性能验证。


## 图生修正（2026-09-19）

首个模型实际渲染不合格：海水底座、斜拉桥塔和斜拉索缺失，并出现车辆。旧模型与预览保留为 `rejected.glb`、`rejected.png`；旧 generationId 为 `65588f8f-0a50-48d4-bb46-50ecbd751b25`。

内置 image_gen 以 concept.png 为视觉参考生成 `asset-reference.png`（1254 × 1254）。图中完整隔离的海面地块、两端岛屿、灯塔和可辨识粗斜拉索用于模型约束；原 concept.png 与 water-texture.png 保持不变。

### 资产参考图提示词

Use case: stylized-concept. Asset type: image-to-3D modeling reference, one complete isolated sea highway environment diorama asset. Reference image 1 is STYLE AND SUBJECT reference only: retain its polished cheerful cartoon 3D look, white cable-stayed bridge over vivid blue sea, green rocky islands and red-roofed lighthouse, but redesign the composition into one small complete isolated model. On a plain neutral light gray studio background, render an entire compact thick rectangular AZURE TURQUOISE SEA-WATER BASE with a white cable-stayed bridge crossing it diagonally between TWO SMALL ISLANDS at the two ends. Most of the base is blue water with simple visible small wave ripples. Two recognizable white A-SHAPED bridge pylons have diagonal legs joined at the apex and clear open triangular spaces. Each pylon supports multiple THICK clearly visible white DIAGONAL CABLE STAYS fanning out to both sides of the roadway; the cables are solid chunky rods suitable for 3D reconstruction, never faint thin lines. Broad gently raised dark gray asphalt bridge deck, white safety railings, red-white curbs. One small white lighthouse with red cap on an island. Camera 45 degree elevated three-quarter view; show every edge of the water-base and the full tops of towers. Center the complete object with generous gray margin around all sides. Simplified clean mobile-game geometry, warm-white highlights, soft studio shadows. No cars, no traffic, no people, no buildings except lighthouse, no land under bridge, no horizon, no sky, no text, no logo, no UI. Exactly one coherent self-contained isolated 3D environment asset, no grid and no multi-view sheet. Square composition.

### 图生模型提示词

Reconstruct the reference image as one complete cheerful cartoon 3D sea-highway diorama. Preserve the vivid thick turquoise-blue WATER BASE covering most of the footprint, TWO white A-shaped bridge pylons and many clearly visible THICK DIAGONAL CABLE STAYS fanning from the tower tops down to both sides of the bridge deck. The bridge crosses WATER, never land. Wide dark-gray gently undulating bridge roadway, white guardrails, red-white curbs, two small green rocky islands at the ends, a single white lighthouse with red cap. All image objects belong to one coherent miniature environment asset. Preserve the original clean cartoon materials and colors and the clear gaps between cable stays. No cars or people, no added buildings, no sky, no background plane, no text.

参考图经 rodin_create_uploads 和 HTTP PUT 成功上传（HTTP 200），本轮仅提交一次带 reference_upload_ids 的图生任务。新 generationId：`787ad4e5-fc3a-4144-aa14-bf5f6dd6606f`；提交状态 queued。参数仍为 Raw / 18000 polygons / Gen-2.5-Medium / GLB。主 Agent 下载并重新渲染验收。
