<div align="center">

# Stoneframe · 石间拼贴

**让石纹、彩绘与色块，组成新的画面。**

从佛像、石窟、古建和壁画摄影出发，<br>
设计带有复古印刷质感的拼贴海报。

[浏览作品](../checked-collage-panel-extractor/examples/GALLERY.md) · [开始使用](#开始使用) · [设计指南](references/design-guide.md)

</div>

| 摄影原片 | AI 拼贴 |
| :---: | :---: |
| <img src="../checked-collage-panel-extractor/examples/originals/DSC09463.jpg" height="320" alt="处理前：完整构图的摄影原片参考"> | <img src="../checked-collage-panel-extractor/examples/artworks/artwork-01.jpg" height="320" alt="处理后：AI 艺术拼贴作品"> |

*摄影原片参考与《朱焰》：石像成为主视觉，岩壁背景被群青与朱红光环重新组织。*

一张照片里，最有表现力的可能是手掌的裂纹、半掩的目光，或一整面重复的佛龛。石间拼贴帮助你找到这个主体，再决定色块、尺度和局部细节如何围绕它展开。

这份 skill 整理了作者的大同摄影与 AI 拼贴实践：从选片、设计简报到提示词和作品检查，供你用于自己的照片。

## 两种创作方向

| 方向 | 画面重点 | 适合的摄影 |
| --- | --- | --- |
| **超现实波普 · Surreal-pop** | 一个巨型元素制造尺度反差，搭配明确的大色块 | 轮廓清楚的单尊雕像、手势、建筑局部 |
| **梦核拼贴 · Dreamcore** | 2–5 个局部片段形成回声，通过重复、灰度与错位组织画面 | 半遮挡面孔、彩绘细节、连续佛龛 |

配色从群青、朱红、金黄、砂金与旧纸米白中组织。石头的体积、风化与彩绘剥落仍是画面的重点。具体构图方法见 [设计指南](references/design-guide.md)。

## 开始使用

把整个 `heritage-photo-collage` 文件夹放入客户端的 skills 目录，再提供照片或可读取的目录。Codex 常用目录是 Windows 的 `%USERPROFILE%\.codex\skills\`，或 macOS / Linux 的 `~/.codex/skills/`。

显示名称是 **Stoneframe · 石间拼贴**，调用标识是 `heritage-photo-collage`。

**先做方案：**

> 使用 $heritage-photo-collage，从我的摄影目录选出 6 张：3 张适合超现实波普，3 张适合梦核拼贴。逐张写设计 brief 和最终提示词，建立长边约 1800px 的 JPEG 工作副本。本轮不生成图片，完成 6 张后停止。

**制作一张海报：**

> 使用 $heritage-photo-collage，以这张照片制作一张方形拼贴。用群青、砂金和米白，保留面部残损与石刻纹理，只增加一个巨型圆环。生成一个版本。

制作图片需要客户端中可用的图像生成工具。只选片、写方案与提示词时，不调用图像生成。

## 你会得到什么

每张设计简报会说明：

- 采用哪张原片，以什么作为主视觉；
- 保留哪些摄影细节，删除哪些可见杂物；
- 配色、画幅、主体位置和留白；
- 一个巨型元素，或 2–5 个有来源的局部片段；
- 一段可直接用于参考图编辑的提示词。

原片保持不变，输出使用工作副本。实际制作后，按原片核对五官、手势、雕刻纹理和残损，注明 AI 艺术再创作。

## 从拼贴到单张导出

如果已经有了满意的多图联系表，使用 [PanelPick · 勾选拆图](../checked-collage-panel-extractor/)：标出想保留的格子，从无标记版导出单张图片与 ZIP。

两份 skill 可以分别安装；同时安装便于衔接创作与选图。

## 作品与说明

[作品集](../checked-collage-panel-extractor/examples/GALLERY.md) 收录 11 张已有 AI 拼贴与 7 张摄影参考。设计指南中的提示词是根据作品风格整理的模板，原始生成提示词未留存。

代码与文档采用 [MIT License](LICENSE)。

---

**English** — Stoneframe guides heritage photo collage design: select a photographic anchor, plan the palette and composition, and write an actionable image-editing prompt. Choose a single oversized element for surreal-pop, or a few sourced detail fragments for dreamcore. Brief-only mode does not invoke image generation.
