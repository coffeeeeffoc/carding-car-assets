# 七彩丹霞生成记录

风格参考：`../../../branding/avatar.png` 的明快圆润卡通 3D；地层采用自然红橙、赭黄、灰绿，不使用霓虹彩虹。

生成顺序：效果图 → 岩石贴图 → 3D 地块。图片均使用内置 `image_gen`，未使用 CLI。模型使用文本描述生成，效果图未上传给 Rodin。

## 效果图 concept.png

Use case: stylized-concept. Asset type: wide landscape environment concept art for an original cheerful cartoon 3D mobile kart racing game. Create a sunlit Seven-colored Danxia geological canyon racetrack in China. Very wide smooth dark asphalt racing road with generous winding curves sweeps through rounded sculptural layered ridges. The ridge strata alternate NATURAL brick red, burnt orange, warm ochre, pale yellow, muted gray-green and cream sediment, clearly geological earth colors, not neon rainbows. Distinct strata wrap around smooth mountain contours. A small wooden scenic observation deck with protective railing and a compact tourist service kiosk sit safely outside the racing road. Steel road guardrails, clear white road edges, sparse desert shrubs. Elevated three-quarter view that clearly shows the road, surrounding terrain and scenic props. Bright blue sky, fluffy small clouds, warm white highlights, polished soft rounded 3D animated-family-game aesthetic, saturated but natural color blocks, readable modular shapes. No vehicles, no racers, no lettering, no UI, no logos, no watermark. Widescreen composition 1536x1024 or wider.

## 岩石贴图 rock-texture.png

Use case: stylized-concept. Asset type: square seamless tileable diffuse/albedo sandstone rock texture for rounded cartoon 3D Danxia canyon terrain in a mobile kart racing game. Create only a flat surface texture, exact straight-on orthographic view, no perspective, no rendered object, no horizon. Broad organic gently undulating horizontal sediment strata of natural brick red, burnt orange, ochre and pale sand, occasional narrow muted gray-green strata, subtle fine sandy grain and shallow stylized erosion seams. Natural geological layer colors, never neon rainbow. Warm playful readable rounded animated-game aesthetic with simplified detail and clear broad color blocks. Equal flat illumination everywhere, no highlights, no cast shadows, no ambient occlusion, no gradient or vignette. All four edges must seamlessly repeat with no visible borders; match color and layer flow across each opposing edge. No text, logos, watermark, plants, road, pebbles or objects. 1024x1024 square material texture.

## 模型 model.glb

Small complete Danxia canyon racing environment diorama on a solid shallow terrain base. Three rounded sandstone ridges with natural geological strata alternating brick red, orange, ochre, pale yellow, cream and muted gray-green, never neon rainbow. Broad smooth dark asphalt S-bend across foreground with white edge lines and metal guardrails. Beside road: compact wooden scenic observation platform with railing, one tiny tourist service kiosk with blue-gray roof, sparse dry green shrubs. Cheerful polished rounded cartoon 3D mobile kart-game style, clean readable large shapes, saturated earth palette and soft warm white highlights. Cohesive terrain tile, all sides and underside modeled, no floating parts. No sky geometry, no text, logos, cars or people. Static visual art prototype; decorative road is not gameplay collision geometry.

参数：`geometry_file_format=glb`、`mesh_mode=Raw`、`quality_override=18000`、`tier=Gen-2.5-Medium`。

第一次参数检查因提示词超过 1024 字符被拒绝，未启动生成；缩短后仅提交一次成功任务，generation ID：`03e64444-9484-4c38-a058-6ca0a5df44e6`。当前队列状态记录在 `asset.json`；根 Agent 统一下载与检查。

## 验证与边界

- 已目视检查两张生成图：无 UI、品牌、水印；自然地层颜色与道路/观景设施符合要求。
- 已读取 PNG 文件头确认：concept.png 为 1536 × 1024（2934427 字节），rock-texture.png 为 1254 × 1254（2619897 字节）。
- 贴图为正视平坦层状纹理，以可平铺为生成目标，实际 UV 拼缝仍需材质导入时验证。
- 模型为静态美术原型，不可作为实际赛道碰撞几何；未经移动端、拓扑、模型分离或 Cocos 导入验收。


## 图生模型修正

初版实际渲染出现过厚方块峡谷、彩层不明显、赛道不清晰，已改名保存为 `rejected.glb` 与 `rejected.png`。原始 generation ID：`03e64444-9484-4c38-a058-6ca0a5df44e6`。

先以内置 image_gen 参考 concept.png 生成完整孤立低厚度地块 `asset-reference.png`，再通过 `rodin_create_uploads` 获取上传地址、HTTP PUT 返回 200 后，将 upload ID 作为 `reference_upload_ids` 提交。新模型仅实际提交一次，参数仍为 18000 / Raw / Gen-2.5-Medium / glb。generation ID：`533a8482-38bd-4530-bdf4-1b01d9f80531`。PNG：1254 × 1254，2382848 字节。新模型待下载渲染验收。

### asset-reference.png 提示词

Use case: stylized-concept. Asset type: isolated 3D game environment model reference, square studio render. Use the provided Danxia concept ONLY as the style and natural geological color reference, redesign its composition into ONE compact self-contained low-thickness terrain diorama fully visible with margins on plain light gray studio background. 45-degree elevated three-quarter view. Three smooth ROUND low Danxia hills and long rounded ridgelines with very clear broad alternating geological stripes: brick RED, burnt ORANGE, ochre YELLOW, cream, and muted gray GREEN. Color strata visibly wrap around all hills, warm playful polished cartoon 3D, large readable color blocks, soft bevels and gentle highlights. A broad unmistakable DARK GRAY ASPHALT S-shaped racetrack passes uninterrupted from one edge of the tile to the opposite edge with distinct white edging and WHITE protective guardrails. Track remains exposed to camera, no hills hide it. One small wooden scenic viewing pavilion beside road. Very thin irregular rounded terrain slab; slab thickness only 1/15 of total footprint width, low hills rise naturally above it. Full asset including slab underside and all silhouette edges fits in frame. NO tall rectangular cliffs, NO canyon box, NO cubic mountains, NO massive vertical walls. No background landscape, no sky, no vehicles, no people, no text, no logo, no watermark.

### 图生 Rodin 提示词

Reconstruct the uploaded image as one complete cartoon 3D Danxia racing terrain diorama. Preserve its THIN base, ROUND hills with red orange ochre cream and gray-green geological color stripes, wide dark asphalt S-bend crossing from edge to edge, white guardrails, and small wooden viewing pavilion. Keep the road clearly visible and continuous. Do not turn it into a box or tall vertical canyon walls. No background plane, no text, people or cars. Static environment visual prototype.
