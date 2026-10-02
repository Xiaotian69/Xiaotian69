<div align="center">

# PanelPick · 勾选拆图

**勾选喜欢的作品，导出独立图片。**

支持青色标记选图、数量核对、单张导出与 ZIP 打包。

[快速开始](#快速开始) · [作品集](examples/GALLERY.md) · [石间拼贴](../heritage-photo-collage/)

</div>

![11 张大同拼贴作品](examples/gallery-contact.jpg)

一张联系表里有很多小图，你只想留下其中几张。PanelPick 读取勾选位置，从对应的无标记拼图裁出作品，交付单张 PNG 和压缩包。

它适合摄影选片、AI 海报筛选和拼贴作品整理。作品内部的白框、插图与纸纹会一起保留；方形输出默认用留白补齐构图。

这组大同拼贴是项目的作品示例。想从自己的照片创作类似海报，可以使用 [Stoneframe · 石间拼贴](../heritage-photo-collage/)；查看 [完整作品与摄影参考](examples/GALLERY.md)。

## 看一组原片与作品

| 摄影原片 | AI 拼贴 |
| :---: | :---: |
| <img src="examples/originals/DSC09298.jpg" height="320" alt="处理前：完整构图的摄影原片参考"> | <img src="examples/artworks/artwork-03.jpg" height="320" alt="处理后：AI 艺术拼贴作品"> |

这张《窟中金面》把眼部、彩绘和卷纹重新组织为拼贴细节。它是已有的 AI 作品；PanelPick 用于从成品联系表中导出选中的格子。[更多原片对比](examples/GALLERY.md)。

## 快速开始

准备两张内容与排列一致的图片：一张画了亮青色勾选标记，一张没有标记。格子应等宽、等高。

在本目录安装依赖，运行命令：

```sh
python -m pip install -r requirements.txt
python extract_checked_panels.py --marked marked.png --clean clean.png --rows 2 --cols 3 --out selected --expected 3 --zip
```

这个例子处理一张 2 行、3 列的联系表，导出 3 张选中的作品。把文件名、行列和数量换成自己的即可。需要 Python 3.10+。

**想先试一下？** 仓库附有可直接运行的示例：

```sh
python extract_checked_panels.py --manifest examples/manifest.example.json --out demo-output --expected 3 --square-mode keep --zip
```

## 在 Agent 中使用

把整个 `checked-collage-panel-extractor` 文件夹复制到客户端的 skills 目录。Codex 常用目录：

- Windows：`%USERPROFILE%\.codex\skills\`
- macOS / Linux：`~/.codex/skills/`

重新加载后，可以直接说：

> 使用 $checked-collage-panel-extractor，按照我的青色勾选标记，从无标记版拼图拆出 11 张。输出 1:1 PNG 和 ZIP，保留内部白框与插图。

客户端中的显示名称是 **PanelPick · 勾选拆图**，调用标识仍是 `checked-collage-panel-extractor`。[SKILL.md](SKILL.md) 也可以交给能够读图、运行 Python 的其他 Agent。

## 导出结果

输出目录包含以下文件：

```text
selected/
├── sheet01_01_r1_c1.png
├── …
├── selection_report.json
└── selected_panels.zip
```

报告记录选中的行列、裁切位置和来源文件。ZIP 包含本轮图片与报告。数量不符合 `--expected` 时不会导出；同名文件已存在时，换一个输出目录再运行。

## 常用调整

| 需求 | 参数 |
| --- | --- |
| 保持每格原比例 | `--square-mode keep` |
| 用白色留白补成方形（默认） | `--square-mode pad` |
| 允许中心裁切为方形 | `--square-mode crop` |
| 本地放大 2 倍 | `--upscale 2` |
| 去掉测量好的外部分隔线 | `--gutter 4`；每格四边各收 4 像素 |
| 指定选中位置 | `--manual "1,1;1,3;2,2"`；行列从 1 开始 |
| 处理多张联系表 | `--manifest batch.json`；见 [示例清单](examples/manifest.example.json) |

手动选格只需要无标记版：

```sh
python extract_checked_panels.py --clean clean.png --rows 2 --cols 3 --manual "1,1;1,3;2,2" --out manual-output --expected 3 --square-mode keep
```

自动去白边 `--trim-white` 默认关闭，因为白色可能是作品的一部分。放大使用 Lanczos 与锐化，不会补出源图没有的细节。

## 使用前确认

标记应是亮青色，例如 RGB `0,200,255`，尽量画在格子内部。脚本通过颜色和图像差异识别新增笔迹；它不会判断对钩形状，青色文字或跨格标记也可能被选中。检测不准时可改用手动行列。

两张图片需要位置一致。等比例缩放可以处理；平移、旋转、裁切或透视变化需要先对齐。不等宽的拼贴布局应使用明确的裁切坐标。

旧版默认中心裁切和自动去白边；要保留旧处理方式，添加 `--square-mode crop --trim-white`。

## 参与改进

遇到问题时，欢迎提供小样、运行命令、预期选格和输出报告。测试命令：

```sh
python -m unittest discover -s tests -v
```

代码与文档采用 [MIT License](LICENSE)。图库中的 AI 作品及摄影来源见 [素材说明](examples/GALLERY.md#素材说明)。

---

**English** — PanelPick exports checked panels from a contact sheet. The annotated sheet identifies the selection; the matching clean sheet supplies the image pixels. It supports manual coordinates, count checks, square padding, local upscaling and ZIP export. Extraction requires no image-generation service or API key.
