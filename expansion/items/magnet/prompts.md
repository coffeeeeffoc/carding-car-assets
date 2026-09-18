# 磁铁 重生成记录

初版已弃用：`8686df17-28ff-47e3-85c1-7919f42c166e`。旧模型与预览保存为 `rejected.glb`、`rejected.png`。本轮每件只提交一次模型生成。

## 参考图

内置 image_gen 生成 `concept.png`；已目视检查独立单件形体，无车辆、轮胎和底台。

Use case: stylized-concept. Asset type: single-object 3D modeling reference. ONE red horseshoe magnet, clean broad U shape with two parallel straight ends, glossy rounded red body and two ivory-white metallic end caps. Magnet lies flat at a slight diagonal, three-quarter elevated camera makes full U silhouette and broad hollow opening clear. Solid chunky but simple toy-like cartoon 3D style, smooth beveled corners, neutral gray studio background with soft light. Entire magnet centered with generous margins. Magnet only: no vehicle, no wheels, no tires, no stand, no base, no pedestal, no handle, no particles, no accessories, no text, no watermark.

## 模型

先通过 rodin_create_uploads 创建上传，再 HTTP PUT 成功（200），最后传 reference_upload_ids 生成。

Create exactly one standalone red horseshoe magnet matching the reference image, a broad smooth U shaped red solid with two ivory white metallic end caps. Preserve the large hollow opening, smooth rounded edges and simple cartoon materials. Do not model gray background. No wheels, tires, chassis, vehicle, stand, base, pedestal, particles or extra objects.

参数：geometry_file_format=glb，quality_override=2000，mesh_mode=Raw，tier=Gen-2.5-Medium。

Generation ID: ac9ad1f2-6d97-4b6a-b8ee-6a649422f0a0

状态：queued；等待主 Agent 下载、渲染和结构检查。
