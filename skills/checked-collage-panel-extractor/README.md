# 蓝色打勾选图拆分 · Checked Collage Panel Extractor

把联系表中打勾的小图，独立拆成单张图片。**用打勾版选位置，从无标记版取像素。** 支持数量校验、手动选格、方形留白、确定性放大和 ZIP 打包。

![11 张大同石窟拼贴作品预览](examples/gallery-contact.jpg)

这组作品来自作者 Xiaotian69 的大同摄影与 AI 拼贴实践。它们展示石雕质感、群青与朱红色块、巨型光环、局部回声插图和旧纸印刷纹理。**11 张效果图是已有 AI 作品；此工具负责拆图，不负责生成这些作品。** 查看 [完整图库与摄影原片](examples/GALLERY.md)、[来源清单](examples/gallery_manifest.json)。想用自己的照片创作同类海报，见配套 [摄影拼贴创作 skill](../heritage-photo-collage/)。

## 安装为 skill

下载本仓库，把整个 `skills/checked-collage-panel-extractor` 文件夹复制到 agent 的 skills 目录。

- Windows Codex：`%USERPROFILE%\.codex\skills\checked-collage-panel-extractor`
- macOS / Linux：`~/.codex/skills/checked-collage-panel-extractor`

若客户端设置了自定义 skills 目录，以该目录为准。重新加载客户端后使用：

> 使用 $checked-collage-panel-extractor，从打勾版和无标记版联系表提取我选中的 11 张，保留内部白框和拼贴细节，输出 1:1 单张 PNG 与 ZIP。不调用图像生成。

其他支持读取 Markdown 指令、运行 Python 的 agent 也可使用 [SKILL.md](SKILL.md)。

## 本地运行

需要 Python 3.10+。进入本 skill 目录：

```sh
python -m pip install -r requirements.txt
```

仓库自带可以直接运行的 2×3 示例，无需生成图片：

```sh
python extract_checked_panels.py --manifest examples/manifest.example.json --out demo-output --expected 3 --square-mode keep --zip
```

示例青色笔迹由本地画线模拟，三个输出来自对应干净版；示例仅用于验证拆分。网格没有外部间隙。下面的单组命令同样适用于 Windows PowerShell：

```sh
python extract_checked_panels.py --marked marked.png --clean clean.png --rows 2 --cols 3 --out selected --expected 3 --zip
```

只给干净版、明确指定行列：

```sh
python extract_checked_panels.py --clean clean.png --rows 2 --cols 3 --manual "1,1;1,3;2,2" --out manual-output --expected 3 --square-mode keep
```

多组输入在 JSON 数组中列出，路径相对 manifest 所在文件夹。每组需要 `clean`、`marked`（或 `manual`）、`rows`、`cols`，并使用不同的 `prefix`。

## 输出和参数

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| `--expected N` | 不指定 | 写文件前验证全批张数；不匹配退出码 3 |
| `--square-mode pad` | pad | 以白色留白补成方形，不裁掉内容 |
| `--square-mode crop` | — | 明确选择中心裁切为方形 |
| `--square-mode keep` | — | 保持每格原比例 |
| `--upscale 1/2/3/4` | 1 | Lanczos 放大加锐化；不是 AI 细节重建 |
| `--gutter N` | 0 | 每格四边各向内收 N 像素；须先测量分隔线 |
| `--trim-white` | 关闭 | 启用去白边启发式；也可能删掉作品白框 |
| `--manual "1,1;2,3"` | 自动检测 | 从 1 开始的行列；覆盖检测 |
| `--zip` | 关闭 | 打包本轮 PNG 和选择报告 |

输出命名如 `sheet01_01_r1_c1.png`，另有 `selection_report.json`；ZIP 为 `selected_panels.zip`。报告记录来源文件名、格数、每格差分检测得分、选择位置和裁切坐标。输出已存在时拒绝覆盖，换一个输出目录再运行。

**兼容性变化：** 旧版默认中心裁切和自动去白边；现在默认补白、保留白边。要使用旧处理方式，显式添加 `--square-mode crop --trim-white`。增强仍是本地操作，不消耗图像生成额度。

## 检测边界

脚本比较对应图片的像素差异，再筛选亮青色新增笔迹，不会把原有群青背景当成勾。它不识别对钩形状；新增青色文字也可能触发。打勾应落在格子内部，避免压在格子边界。检测不准时检查报告并用 `--manual`。

等比例缩放可自动对齐；裁切、平移或视角变化需要预先对齐。白边与艺术白框无法仅凭颜色可靠区分。脚本只适合等分规则网格，不适合错落拼贴布局。

## 开发与复现

```sh
python -m unittest discover -s tests -v
```

测试覆盖蓝色背景排除、从干净版获取像素、白框保留、数量失败时零导出、选格越界、重复选格、重名覆盖和 ZIP 内容。

欢迎提交可复现的问题：提供不涉及隐私的小样、运行命令、行列号、预期张数与报告。风格实践指南在 [配套 skill](../heritage-photo-collage/)，不会作为精确拆图的生成式后门。

## English

A reusable agent skill and Python utility for exporting checked panels from contact sheets. The marked sheet determines selection; the matching clean sheet supplies every output pixel. Bright cyan annotations are detected with color filtering **and** image differencing, so existing blue artwork is excluded.

Defaults preserve artwork: square padding, no automatic white-border trimming, no upscaling. Count checks and collision checks run before export. Manual 1-based coordinates work without a marked sheet. The included runnable example selects three cells; the historical gallery contains eleven AI artworks and photographic source references. No image-generation service or API key is required for extraction.

## License

代码与文档沿用 [MIT License](LICENSE)。示例照片与 AI 作品由 Xiaotian69 提供，作者及来源见图库清单；图片不是对文物现状的记录或考据资料。
