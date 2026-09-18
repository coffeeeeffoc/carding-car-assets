# 西瓜皮 重生成记录

初版已弃用：`7bebb28c-84ca-4c8b-9d62-83d1719cebd8`。旧模型与预览保存为 `rejected.glb`、`rejected.png`。本轮每件只提交一次模型生成。

## 参考图

内置 image_gen 生成 `concept.png`；已目视检查独立单件形体，无车辆、轮胎和底台。

Use case: stylized-concept. Asset type: single-object 3D modeling reference. A single eaten watermelon rind, a THIN curved crescent strip, green striped outer skin, cream-white inner layer with only tiny thin traces of red remaining fruit along its rim. Concave inside is hollow and clearly visible from slightly elevated three-quarter view, rind lying naturally on one side. The whole object fits inside a clean neutral gray studio background, centered, rounded cartoon 3D render with simple clean materials and readable silhouette. This is ONLY the empty watermelon rind, no solid red wedge, no full fruit flesh, no board, no tray, no stand, no pedestal, no chassis, no wheels, no tires, no vehicle, no text, no watermark. One object only.

## 模型

先通过 rodin_create_uploads 创建上传，再 HTTP PUT 成功（200），最后传 reference_upload_ids 生成。

Create exactly the single eaten watermelon rind in the reference image. A thin curved hollow green striped rind with cream white interior and only thin red flesh remnants on the edge. Keep its crescent silhouette, hollow interior and rounded cartoon material. Model the rind alone, not the gray background. No solid fruit wedge, no base, tray, cutting board, wheels, vehicle or pedestal.

参数：geometry_file_format=glb，quality_override=2000，mesh_mode=Raw，tier=Gen-2.5-Medium。

Generation ID: 30a80b4f-3ece-4b5b-ad9f-9bafcf6d966a

状态：queued；等待主 Agent 下载、渲染和结构检查。
