# 冰川道路素材

`road.png`：内置 imagegen 生成的独立冰雪道路底色纹理，2026-09-19。正交俯视、钢蓝色压实冰面、细霜和纵向擦痕，无道路标线、透视、光影或文字。仅作为颜色纹理，镜面高光由 Cocos 标准材质和环境光照计算。

`road.jpg`：游戏运行版，1024×1024、JPEG 质量 88、双三次缩小，保留原图。只有此文件由构建同步到游戏；Power-of-two 尺寸支持移动端平铺与 mipmap。

冰壁继续复用 `runtime-expansion/textures/glacier.jpg`。冰拱、冰壁、积雪和远山由游戏 `GlacierGeometry.ts` / `GlacierSample.ts` 生成，保留几何法线；不经过旧的 unlit GLB 导出流程。此素材用于整条约 1.23 公里的冰川赛道。
