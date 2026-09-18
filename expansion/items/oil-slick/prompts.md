# 油渍 重生成记录

初版已弃用：`c186b8fa-c8f2-4e16-9e4c-19e7bacefbbc`。旧模型与预览保存为 `rejected.glb`、`rejected.png`。本轮每件只提交一次模型生成。

## 参考图

内置 image_gen 生成 `concept.png`；已目视检查独立单件形体，无车辆、轮胎和底台。

Use case: stylized-concept. Asset type: single-object 3D modeling reference. ONE extremely thin flat irregular puddle of spilled oil on neutral light gray background. Camera almost top-down with a very slight three-quarter angle so its wafer-thin edge is visible. Compact organic lobed silhouette, mostly glossy dark black with delicate purple blue iridescence at the edges, a few broad soft reflection shapes. Stylized rounded cartoon surface, simple clear form. Oil surface hugs an imaginary flat ground; thickness is tiny relative to its width, like a spill not a slab. Entire puddle visible centered with margin. No container, no can, no bucket, no tire, no wheel, no vehicle, no supports, no pedestal, no rectangular base, no island, no floating objects, no text or watermark. Only the irregular puddle is the subject.

## 模型

先通过 rodin_create_uploads 创建上传，再 HTTP PUT 成功（200），最后传 reference_upload_ids 生成。

Create only the single irregular oil spill from the reference image, a nearly flat wafer thin puddle mesh with glossy black surface and subtle violet blue iridescent edge. Preserve organic silhouette. Width at least 60 times thickness. Do not model gray background. No container, plate, foundation, wheels, vehicle, support or pedestal.

参数：geometry_file_format=glb，quality_override=2000，mesh_mode=Raw，tier=Gen-2.5-Medium。

Generation ID: 36e63d12-6058-4977-bfbc-2664049519ad

状态：queued；等待主 Agent 下载、渲染和结构检查。
