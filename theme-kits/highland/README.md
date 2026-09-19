# 高原与高山运行模块

针对 `expansion/scenes/highland/concept.png` 准备三个任意路线可复用的模块。源 GLB 保持不变；连续路基由游戏根据所选路线生成，不使用模型自带道路。

```powershell
python assets/carding-car/build-highland-props.py
python assets/carding-car/build-highland-props.py --check
node assets/carding-car/theme-kits/highland/render-previews.mjs
```

`build-highland-props.py` 的无参 `build()` 生成三个 `runtime-expansion/props/highland-*.glb` 及本目录 `manifest.json`，返回 `models` 条目列表，供共享构建入口合并。原始雪峰来自 `expansion/scenes/highland/model.glb`，沿水平面裁切并插值 UV，舍弃微小断片；近景岩壁与驿站为脚本制作。三个模型底面为零，米制，所有贴图内嵌，每件一次 draw call，总计 177,592 字节。

`highland-*.png` 是本目录渲染脚本实际加载 GLB 的预览；`render-check.json` 记录三角面、尺寸与 draw call。已实际目视检查，不以效果图冒充模型或游戏画面。灰岩柱和驿站使用合并调色板纹理；雪峰保留原图预着色。雪峰裁切底部适合作远景，并由较近岩岭遮挡边界，不用作近景可行走山体。
