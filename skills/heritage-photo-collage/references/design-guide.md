# 配色、构图与 prompt 指南

这是基于现有 11 张成品的视觉分析和新增创作模板。历史对话只确认蓝色勾选与单张导出的需求，没有原始生成参数。

## 三套配色

| 方案 | 建议色值 | 适用理由 |
| --- | --- | --- |
| 群青／朱红／金黄 | #1235A5 / #EF3423 / #FFC52F | 清晰剪影、大尺度光环和强对比，适合 surreal-pop |
| 群青／砂金／米白 | #173EA6 / #C89757 / #F1E5CD | 让原石与彩绘成为主角，适合低光石窟和局部回声 |
| 朱红／炭黑／旧纸米白 | #B82E25 / #22201E / #E7D7B9 | 适合人物少、建筑节奏强的照片，使用灰度回声控制密度 |

色值用于描述版式方向，不能把石头皮肤统一涂成这些颜色。保留摄影明暗和体积；纸纹与印刷磨损只能覆盖到仍能读出石刻细节的程度。

## 布局语法

- 主体通常占画面约 55–75%，一条主要视线或对角线组织阅读顺序。
- 圆环放在主体之后，避免穿过脸部；曲线纹样沿空白边侧生长。
- echo 小框共用约 1% 画宽的米白边线，主图与框之间留呼吸空间。
- 小框内容必须有来源：眼部、手势、供器、局部佛龛、剥落彩绘。同一 fragment 的彩色和灰度可构成回声，但不能无限复制。
- 印刷颗粒、套色错位、纸纹是辅助层。避免塑料表面、液态金属、现代广告文字和虚构铭文。
- 文件名含“敦煌”是生成工具的历史命名，不是拍摄地点依据。这批摄影目录是大同，无法单凭文件名判定具体石窟或年代。

## 可直接改写的 surreal-pop prompt

> Edit the supplied photograph into a square editorial heritage photo collage. Keep the photographed sculpture as the main anchor in the right two thirds, preserving its recognizable facial proportions, original gesture, stone erosion, cracks, missing material, carved robe folds and natural photographic light. Add exactly one oversized flat vermilion flame-shaped halo behind the head, spanning roughly 80% of the canvas width, against an ultramarine field. Keep the figure sandstone-colored, with restrained old-paper grain and subtle screen-print wear on the background. Maintain a calm lower-left negative space; no inset panels in this version. Remove only the visible modern fixture identified in the brief. Do not reconstruct missing ancient features, change the face, add fingers, invent inscriptions, add text or watermarks, or smooth the stone into plastic. This is an artistic reinterpretation, not archaeological restoration.

以上位置是模板；按照片视线改写。模板中的删除项需替换成实际可见杂物，没有杂物就删除该句。若照片原有背光已经适合作为设计层，优先保留，不要再叠一个巨型元素。

## 可直接改写的 dreamcore prompt

> Using the supplied grotto photograph as the source, make a square quiet dreamlike photographic collage. Preserve the partial golden face with blue curls emerging from behind the carved painted ledge; keep the original occlusion, eye shape, surface loss, rocky cavity and faded bird relief. Use ultramarine, muted sandstone gold and aged ivory. Place the main face slightly left of center, with the ledge occupying the lower quarter. Use exactly three echo fragments sourced from this same photo: a wide monochrome eye crop in the upper-right ivory frame, a small color crop of the worn bird relief at mid-right, and a circular close-up of an existing blue curl near the lower-right edge. Keep the fragments smaller than the main face and the borders consistent. Add restrained paper texture and a small visual offset to the echoes, while leaving the main photograph sharp. Do not introduce unrelated statues, repair damage, uncover hidden anatomy, invent carvings, add text or watermarks, or create multiple dominant symbols. Label the result as an artistic reinterpretation.

## 来源与诚实交付

摄影原片、AI 成品、精确裁切结果分别注明。生成图和原片即使高度相似，也不能声称有完整像素一致性。新写的 prompt 标为“建议 prompt”；没有历史记录的参数不能伪造为作者原始设置。

生成式工具一次按约定张数输出。零生成模式只写方案、建立副本或小型联系表；不用任何生成、生成式补画或自动扩图调用。
