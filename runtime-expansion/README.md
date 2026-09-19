# 扩展运行素材

此目录由 `python build-expansion.py` 重建，原始 `expansion/` 保留不动。
仅校验：`python build-expansion.py --check`。依赖 Python 3、Pillow，复用现有 `build-mobile.py` 的 GLB 解析。

- `scenes/`：7 个 18,000 三角面的地块缩为最长水平边 36 米，仅作远景地标。道路几何和碰撞由游戏生成。
- `vehicles/`：10 辆车，Y 向上、+Z 为车头、底面 Y=0，长 2.9 米、宽不超过 2.16 米。六辆封闭车型仅在衍生版切出小敞篷座舱，原件不动；按 `driverMount` 放置角色，不能统一放在车顶。
- `drivers/`：10 位坐姿车手，保留源模型的头部、头盔和纹理；圆润程序化身体有 Helmet、Torso、Left/Right 肢体等独立节点。高 1.06 米、臀部约 Y=.32，脚向 +Z。它们是可变换的刚性部件，没有骨骼或蒙皮动画。
- `items/`：12 个道具模型；触发、碰撞、持续效果由游戏负责。所有模型落地，拾取物的悬浮由游戏控制。
- `props/`：11 种独立布景模块，尺寸见 manifest。新增高原雪山、灰岩悬崖与红顶山屋，由 `build-highland-props.py` 生成；总构建会调用该脚本，预览和专属校验记录在 `theme-kits/highland/`。原冰拱净宽 12 米、桥塔净宽 18 米，只适合满足净空的布景，不能替代物理道路；游戏中的自适应桥体另按当前路线生成。
- `textures/`：7 张最大 512 像素 JPEG 环境材质；它们是原候选图的压缩副本，不承诺无缝平铺。城市是路面纹理，其他含岩石、冰、水、草地，勿把全部纹理当沥青铺路。

`manifest.json` 的 `models` 与 `textures` 均用 `file` 表示相对目录路径，附 SHA256、字节数；模型附 `bounds: [min,max]`、来源哈希和用途。所有 GLB 的场景名等于文件名，适配 Cocos 的 `expansion/{category}/{id}/{id}` Prefab 路径。

纹理使用内嵌 JPEG。材质统一 unlit；导出会移除无用法线并精确焊接相同 POSITION+UV 顶点，不丢弃可见三角面、不合并 UV 接缝。需要灯光时应从源模型重新导出法线。车轮仍与车身一体；车手动作需要游戏对独立节点做动画，源站姿人物没有直接放进车体。

实际模型与 10 组车型/车手组合渲染：从 small-games 根目录运行 `node assets/carding-car/render-runtime.mjs`。可用 `PLAYWRIGHT_EXECUTABLE_PATH` 指定 Chrome，`CARDING_PREVIEW_PACKAGE` 指定已有 Three.js/Playwright 依赖的 package.json。输出到忽略目录 `runtime-review/`，不是构建资源；运行包校验上限 12 MiB。
