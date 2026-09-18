# 咔叮唓 · 扩展素材库

本批先准备美术资产，未接入运行时玩法。统一采用现有头像的明快卡通 3D 风格：圆润大轮廓、清晰色块、暖白高光，原创设计，无品牌和文字。

## 范围

- 7 个场景：城市、沙漠、冰川、跨海高速、七彩丹霞、高原与高山、青藏高原草原与小山。每个场景由独立子 Agent 先生成效果图，再生成场景素材。
- 10 种车型：经典卡丁、方程式、拉力掀背、沙漠越野、复古跑车、肌肉跑车、未来电动、迷你皮卡、冰原越野、流线超跑。
- 10 种车手：橙白新秀、蓝色技师、红色竞速手、沙漠探险者、冰原向导、紫色未来车手、绿色巡护员、青色飞行员、粉色街头车手、黑金冠军。
- 12 种道具：氮气瓶、加速板、路障、西瓜皮、油渍、冰冻球、护盾、磁铁、弹簧板、修理箱、金币、随机道具箱。

## 交付约定

各资源保存独立目录及生成记录；`concept.png` 是效果图，`model.glb` 是静态美术源模型，贴图为独立 PNG。Hyper3D 模型仅作视觉资产，未经碰撞、拓扑、绑定、轮胎分离、移动端预算与 Cocos 导入验证，不能据此宣称可直接上架。车手模型先按站姿静态原型准备（实际姿态以模型预览为准），后续绑定、坐姿与动作另做。

场景模型是环境地块/美术原型，赛道碰撞仍应复用游戏的 `TrackBarriers.ts`；模型不得作为当前物理赛道来源。资源统一保存在独立 `carding-car-assets` 仓库的 `expansion/`（small-games 中为 `assets/carding-car/expansion/`），避免重复提交到游戏目录或自动进入小游戏首包。

完整清单、实际状态及预览见 [catalog.json](catalog.json) 和 [index.html](index.html)。每项生成提示词、来源与验证结果写入相邻记录。

## 本批交付

已保存 39 个 GLB：7 个场景地块、10 辆车、10 位车手、12 个道具，合计约 138.5 MiB；每项均有实际模型渲染 `preview.png`。另有 7 张场景效果图、7 张场景材质候选图，以及修正资产使用的建模参考图。场景效果图展示目标美术方向，GLB 预览展示实际交付质量，两者不能互相代替。

| 场景 | 独立子 Agent | 素材目录 |
| --- | --- | --- |
| 城市 | scene_city | scenes/city |
| 沙漠 | scene_desert | scenes/desert |
| 冰川 | scene_glacier | scenes/glacier |
| 跨海高速 | scene_sea_highway | scenes/sea-highway |
| 七彩丹霞 | scene_danxia | scenes/danxia |
| 高原与高山 | scene_highland | scenes/highland |
| 青藏高原草原与小山 | scene_tibetan_grassland | scenes/tibetan-grassland |

7 个场景均先生成效果图，再制作贴图与模型。图片使用内置 image_gen，38 个最终模型来自 Hyper3D Rodin Gen-2.5；弹簧板因生成结果丢失螺旋结构，使用项目已有 Three.js 按参考图建模，保留 Base、Coil、Top 三个独立网格和可复现脚本。失败版本未计入交付，原任务 ID 保留在生成记录中。

已检查全部 GLB 可解析、内嵌资源、三角面数量、文件哈希唯一性，并实际加载渲染和目视检查。场景各 18,000 三角面，车型和车手各 5,000，道具通常 2,000，弹簧板 2,520。它们仍是静态美术源：场景中的地形、跑道、建筑为整体网格；车轮未拆出；车手未绑定；生成时的比例与轴向需接入时统一。跨海地块是桥段，海面与桥尾边界需在场景装配时延展。贴图已验图片格式，尚未验游戏内 UV 重复接缝。

## 复核

从本素材仓库根目录运行：

```powershell
python expansion/check-assets.py --complete
```

上述命令检查 39 项交付，并重建清单和离线预览页；若从 small-games 根目录执行，使用 `python assets/carding-car/expansion/check-assets.py --complete`。渲染脚本复用工作区已经安装的 Three.js 与 Playwright，不新增依赖；从素材仓库运行时，把 `CARDING_PREVIEW_PACKAGE` 指向已安装这些依赖的项目的绝对 `package.json` 路径（例如 small-games 的 `games/local/travel-bund/package.json`），必要时用 `PLAYWRIGHT_EXECUTABLE_PATH` 指定系统 Chrome。

```powershell
node expansion/render-previews.mjs
node expansion/items/spring-pad/make-model.mjs
```
