# 冰川场景生成记录

统一参考 `art-source/branding/avatar.png` 的明快卡通 3D 风格。先完成效果图，再生成纹理与模型。内置 image_gen，每项单独生成；模型 Hyper3D 文生 3D，未上传效果图。

## concept.png

Use case: stylized-concept. Asset type: wide environment concept art for an original Chinese mobile kart racing game, glacier stage. Primary request: a sweeping glacier canyon race track: chunky translucent ice-blue canyon walls, a broad ice-cave arch opening that the road passes through, rounded snow-capped peaks, one small orange-and-cream polar research cabin beside the road with simple antenna. A broad legible blue-grey paved race track enters foreground and gently curves through the ice arch into the distance; orange and white striped safety barriers continuously outline the road. Style: premium cheerful cartoon 3D, rounded bold silhouettes, clear saturated color blocks, glossy yet readable stylized materials, warm white sun highlights and soft ambient shadows; same approachable toy-like racing world as a glossy orange-and-white kart game. Wide 16:9 composition, three-quarter environment view at roadside height, foreground road clear, cyan sky and soft clouds. Environment only, no kart, no drivers, no HUD, no lettering, no logos, no watermark. Attractive finished environment visualization, not a grid, not a texture sheet.

## ice-texture.png

Use case: stylized-concept. Asset type: one seamless tileable base color texture for glacier surfaces in a cheerful premium cartoon 3D kart racing game. Primary request: square 1024x1024 blue glacier ice texture, perfectly flat orthographic top-down view filling every pixel edge to edge. Medium cyan and pale ice-blue translucent-looking color fields with sparse soft white irregular frost veins and subtle rounded polygonal crystalline patches. Uniform diffuse illumination, no directional shadow, no baked highlights, no gradient, no horizon, no perspective, no objects, no snow piles, no road, no symbols, no text, no grid, no border. Restrained low contrast, readable large shapes, no dense photorealistic noise. Opposite edges should match for continuous seamless tiling. A usable game surface material texture, not a scene and not a material sphere.

## model.glb

A complete compact stylized cartoon 3D glacier kart racing environment diorama on a thick snowy blue-ice terrain base. One broad blue-grey racetrack bend sweeps across the base and passes through a chunky translucent cyan ice arch in the central glacier wall. Continuous orange and white safety barriers outline both sides of the road, leave the driving surface clear. Snow capped glacier cliffs and rounded snowy mountain peaks behind the track. One small orange and cream polar research cabin with dark windows and a simple antenna to one side. Cheerful polished toy-like 3D game art, rounded large silhouettes, saturated cyan and white with small orange accents, warm sun highlights, readable shapes. Complete isolated solid scene chunk, no sky dome, no water plane, no people, no cars, no letters, no logos. Static environment prototype, one cohesive terrain diorama.

参数：`quality_override=18000`, `mesh_mode=Raw`, `tier=Gen-2.5-Medium`, `geometry_file_format=glb`。

仅作静态美术源场景地块；碰撞、Cocos 导入和移动端性能尚未验证。纹理按可平铺要求生成，接缝需接入材质时复核。
