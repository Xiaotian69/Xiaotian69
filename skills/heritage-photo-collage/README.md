# 古建与雕塑摄影拼贴 · Heritage Photo Collage

从自己的佛像、石窟、古建和壁画照片出发，做成保留摄影质感的复古拼贴海报，或先获得可执行的设计 brief。

这份 skill 是根据作者的 [11 张历史作品](../checked-collage-panel-extractor/examples/GALLERY.md) 整理的创作方法。聊天记录没有保存最初的生成 prompt；这里的方案是对现有风格的整理与补充，不宣称能够复现原图。

把本文件夹复制到 agent 的 skills 目录，用以下指令开始：

> 使用 $heritage-photo-collage，扫描我的摄影目录。选 3 张适合 surreal-pop、3 张适合 dreamcore 的照片。每张写完整设计 brief 和最终 prompt，输出长边约 1800px 的 JPEG 工作副本。不调用图像生成，不修改原片，完成 6 张后停止。

需要实际制作时，明确提供照片、张数和画幅，例如：

> 使用 $heritage-photo-collage，以这张原片制作一张 1:1 群青、砂金、米白的摄影拼贴。保留面部残损和石刻纹理，只增加一个巨型背光圆环。生成一个版本。

[SKILL.md](SKILL.md) 负责判断模式与流程；[设计指南](references/design-guide.md) 提供具体配色、构图和 prompt 模板。图像生成需要客户端可用的图像工具；仅写 brief 不需要图像 API。

精确拆分已有拼图请使用 [蓝色打勾拆图 skill](../checked-collage-panel-extractor/)。两者可以独立安装；同时安装可直接衔接创作与选图导出。

代码与说明沿用 [MIT License](LICENSE)。图库由作者提供；AI 海报用于艺术展示。
