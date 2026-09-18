# 沙漠场景生成记录

生成顺序：先效果图，后地面纹理，最后场景模型。图片使用内置 image_gen；模型使用 Hyper3D Rodin。现有 branding/avatar.png 仅作风格观察，未上传。模型按下述提示词生成，未上传效果图。

## 效果图

Use case: stylized-concept. Asset type: wide environment concept image for an original mobile kart racing game. Create a polished cheerful stylized 3D desert race circuit, landscape 16:9 composition, elevated three-quarter camera clearly showing a broad dark asphalt S-bend road passing through golden rolling sand dunes. Rounded amber wind-eroded rock towers, a compact turquoise oasis with palm trees, a simple cream sandstone roadside supply-station building with orange shade canopy, no branding. Red-and-white curbs and sturdy gray low safety guardrails describe the entire visible S-bend clearly. Distant desert mesas, rich blue sky, a few soft white clouds, warm noon sunlight and warm-white highlights. Large rounded forms, readable clean color blocks, inviting toy-like premium cartoon game rendering consistent with a glossy orange-white chibi kart game's art direction. Empty track with no cars or characters. Crisp terrain and buildings. No UI, no lettering, no logos, no watermark, no photoreal grit. This is an environment effect image before asset creation.

## 地面纹理

Use case: stylized-concept. Asset type: seamless square terrain base-color texture for an original cheerful cartoon 3D mobile desert kart racing game. Generate a perfectly top-down orthographic close view of fine golden desert sand, flat material swatch completely covering all edges, softly stylized tiny sand grains and delicate wind ripples with restrained variation. Warm pale ochre and golden cream palette matching a bright noon desert; no perspective, no horizon, no large dunes, no rocks, no vegetation, no objects, no footprints, no text, no border, no shading gradient, no directional cast shadows, no baked specular highlight. Uniform diffuse illumination, subtle readable details suitable for repeating on large 3D terrain surfaces. All four edges designed to tile seamlessly. Square 1024 x 1024.

## 场景模型

A single complete cheerful stylized cartoon 3D desert racing environment terrain diorama static prototype. Rectangular sandy ground tile, rolling golden dunes, rounded amber wind-eroded stacked rock towers, a small turquoise oasis pond with a few chunky palm trees, one simple cream sandstone supply-station building with an orange canopy. A broad dark asphalt S-bend track crosses the terrain, red and white curbs, gray low safety guardrails with posts follow both curves. Large rounded readable shapes, toy-like mobile kart racing aesthetic, warm-white highlights, vibrant golden sand, emerald palms and turquoise water. Full scene contained on one terrain base. No cars, no people, no text or logos, no sky mesh, no backdrop. PBR colored materials. Environment artwork prototype only; no collision geometry needed.

Parameters: geometry_file_format=glb, mesh_mode=Raw, quality_override=18000, tier=Gen-2.5-Medium.

Generation ID: 9163c7a9-ccbb-4ed4-881d-594b4d2eb816.

## 使用范围

图片检查：concept.png 为有效 PNG，1672 × 941，2,223,283 字节；ground-texture.png 为有效 PNG，1254 × 1254，2,921,339 字节。已目视检查效果图：空赛道、S 弯护栏、沙丘风蚀岩、绿洲与补给站可辨，无文字和 UI；纹理为俯视细沙。

效果图作为视觉方向；地面纹理为生成的平铺候选，重复接缝需在正式地形材质中复核。场景模型为静态美术原型，不用于当前跑道碰撞，未作 Cocos 导入、移动端预算、模块拆分和碰撞验证。


## 完整地块参考图修正

初版模型实际渲染只有绿洲、沙地及植物，缺少宽阔赛道和补给站，弃用 generation `9163c7a9-ccbb-4ed4-881d-594b4d2eb816`，保存 rejected.glb / rejected.png。

内置 image_gen 读取 concept.png 作风格参考，生成 asset-reference.png（1536 × 1024，2,172,380 字节），目视检查完整地块、宽 S 弯、双侧护栏、两根岩柱、绿洲与补给站均可辨，无车辆文字。

### 参考图提示词

Use case: stylized-concept. Create a new 3D modeling reference image using the supplied desert concept image ONLY as a style and palette reference. Subject: ONE complete isolated SOLID low terrain diorama of a desert race circuit. Entire terrain base and all objects fully in frame, generous margin, plain light-gray studio background, no sky or horizon. Camera at 45-degree downward isometric view. MOST IMPORTANT: a clearly visible wide dark-gray ASPHALT S-BEND ROAD crosses the terrain from the front-left edge to the rear-right edge; asphalt is an obvious distinct raised road surface at least one-third of terrain width, with continuous chunky red-and-white safety barriers bordering BOTH edges along both curves. Road is not buried by sand or blocked by any object. Golden rounded LOW sand dunes on a low solid rectangular sand terrain base, exactly two chunky amber wind-eroded rock pillars, one small turquoise oasis with two palms, and ONE clearly recognizable low cream-white roadside supply station building with orange awning, doorway and windows. Place the supply station beside the track visibly separated from the rock pillars, large enough to recognize. Restrained detail, rounded cartoon 3D toy-like forms, warm clean colors matching the reference. No vehicles, people, text, UI, logos or floating decorations. This must look like a complete buildable miniature circuit asset, not a landscape crop or open background.

### 图生模型提示词

Reconstruct this complete isolated desert circuit terrain diorama from the reference image. Essential geometry: a clearly visible BROAD dark gray asphalt S-bend road crossing from front-left to rear-right, continuous safety barriers and red-white curbs bordering BOTH road sides along its full length; one cream low supply-station building with orange awning beside the road. Also preserve the solid low golden sand terrain base, two wind-eroded rock pillars and small turquoise oasis with palms. Road and building must be present and remain dominant recognizable features. Full complete asset; round clean colorful cartoon materials. No vehicles, characters, text, sky or background plane. Model all the reference terrain as one environment static prototype; do not reduce it to an oasis only.

上传流程：rodin_create_uploads -> HTTP PUT（200）-> reference_upload_ids。仅一次新任务。参数：glb / 18000 / Raw / Gen-2.5-Medium。

新 Generation ID: 192ceb89-dec8-4f5e-b951-2ff863c73744

状态：queued，模型下载及渲染验收由主 Agent 继续。
