# GTA Thumbnail Pro 🎮

**AI-powered GTA 6 thumbnail design Skill | 内容驱动的 GTA6 游戏视频封面设计 Skill**

[中文说明](#中文说明) · [English](#english) · [Installation](INSTALL.md) · [Release notes](RELEASE_NOTES.md)

> **Design the visual story first — not just a title over a screenshot.**
>
> 先想清楚观众应该在画面中看到什么，再决定文字如何排版。

**Status:** `v2.8.0-beta` · Initial public beta / 首发测试版本

## 中文说明

GTA Thumbnail Pro 是一套面向 **B站 / 小红书 / YouTube** 的视频封面设计工作流。它不是独立的 AI 生图服务；它通过 Skill 规则与结构化生成指令，帮助兼容的 AI 工作环境理解视频看点，设计更有内容表现力的封面，再利用已有图像工具执行。

### 主要能力

- **内容驱动视觉构思**：先分析点击动机与画面要传递的故事，再安排主体、景别、空间和信息层次。
- **12 套可区分的视觉风格**：电影叙事、悬念探索、对比、超大数字、多图拼贴、背景巨字、荒诞名场面、快讯、地图攻略、复古杂志、原生奇观、极简氛围。
- **A/B/C 独立创意方案**：默认规划不同的整图结构，不是同一张底图更换三个字幕位置。指定风格时，三方案在该风格内变化。
- **标题冲击力**：支持原文准确保留、主词突出、字阶、描边和空间层次；文字效果服从画面设计。
- **真实本人照片保护**：未明确授权时不重新生成真人脸部、发型、身体或表情；支持可用工具下的非生成式抠图与原像素图层合成。
- **内容参考知识库**：涵盖 B站 8 类、小红书 7 类内容；YouTube 使用基础平台设计规则，不宣称该手册有独立的完整热门样本数据。
- **离线 HTML 排版编辑器**：`tools/thumbnail-editor.html` 提供可编辑标题等本地编辑与导出能力；不能代替 AI 生图或自动抠图。

### 快速使用

1. [下载 `v2.8.0-beta` Release 中的 Skill ZIP](https://github.com/Tingxiao-Wang/gta6-thumbnail-skill/releases) 并解压，保留 `SKILL.md` 及文件夹的相对路径。
2. 将 `gta-thumbnail-pro` 文件夹导入支持自定义 Skill 的 AI 工作环境，或按该宿主要求加载 `SKILL.md`。WorkBuddy、Codex、豆包的具体入口和图片工具能力可能不同。
3. 提供平台、视频看点和**准确封面文字**。上传图片时说明是主体素材、风格参考，还是两者兼用。
4. 让 Skill 规划 A/B/C 三套**不同画面**；如宿主可生图，分别执行三个方案；无法执行时只输出设计与提示词，不虚构已出图。
5. 如标题中文字不准确，打开 `tools/thumbnail-editor.html` 调整文字图层并导出。

**可复制的首发测试指令：**

```text
为 B站制作 GTA6 剧情深度解析封面，标题必须准确保留：
「万字解析：GTA6到底讲了什么故事？」
请使用 v2.8.0-beta 的视觉创意导演先规划视觉故事，再输出 A/B/C 三个整张画面不同的方案。
要求有实际意义的非文字视觉设计，不能只在同一张背景底部添加一行字幕。
不得编造“全网首发”、评分、游戏剧情事实或未提供的图像证据。
```

### 本地验证（仅检查规则与指令，不生成图片）

Python 3、标准库即可运行：

```bash
python tests/test_v28.py
python tests/test_v272_person_photo.py
python tests/test_v252_intake.py
python tools/compile_brief.py --brief examples/v28_story_retest/input.json --out output-v28
```

在 `output-v28` 中检查 `prompt-A/B/C.txt` 和 `editor-project-A/B/C.json`。**脚本测试通过 ≠ 实际封面质量超越原生生图**；请参阅 [真实成品对照测试](tests/V28_MANUAL_COMPARISON.md)。

## English

GTA Thumbnail Pro is a **content-first design Skill** for GTA 6 video covers and thumbnails. It guides an AI host through the **visual story → scene composition → information hierarchy → typography** workflow, rather than merely adding one line of text to a game screenshot.

### Features

- **Creative-director workflow:** understand the viewer's click motive before composing a frame.
- **12 independent visual languages:** cinematic story, mystery, comparison, big number, editorial collage, background typography, absurd moment, breaking news, tactical guide, retro magazine, native spectacle, and minimal atmosphere.
- **Independent A/B/C concepts:** different scene structures, not simple font or subtitle variations.
- **Typography direction:** exact user text, multi-level hierarchy, visual emphasis and editable title effects.
- **Real-person photo guard:** do not regenerate an uploaded person's identity or appearance without a specific request. Actual non-generative cutout and compositing require a capable host/tool.
- **Platform-aware output:** Bilibili, Xiaohongshu, and YouTube. Source research coverage is not equally deep across platforms.
- **Offline HTML editor:** local text/composition adjustments; no bundled image generation model or background-removal engine.

### Quick start

1. Download the standalone Skill ZIP from the GitHub Release and extract it.
2. Import the complete `gta-thumbnail-pro` directory into a host supporting custom Skills, or load its root `SKILL.md` according to that host's instructions.
3. Specify the target platform, content hook, exact title, and which uploads are subjects vs. style references.
4. Request three distinct **whole-frame visual concepts**. The host must actually render each concept; the bundled scripts do not generate images.
5. Refine editable typography with `tools/thumbnail-editor.html` when needed.

**Developer validation:** `python tests/test_v28.py` checks prompt generation and policy routing, not rendered-image quality.

## Repository structure / 目录

```text
SKILL.md                         Main Skill instructions / 核心入口
scripts/                         Content, creative-director, role and photo-protection logic
styles/S01.json ... S12.json     Style rules / 十二风格
references/                      Content atlas and visual design principles
assets/                          Original abstract layout mockups (not gameplay screenshots)
tools/thumbnail-editor.html      Offline HTML editor / 离线编辑器
tests/                           Current regression tests and manual QA checklist
INSTALL.md                       Setup instructions / 安装说明
RELEASE_NOTES.md                 Beta changes / 版本说明
```

## Known limitations / 已知限制

- **Not a standalone AI image generator.** Generation, editing, background removal, and multimodal image handling depend on the host and its permitted tools.
- A text prompt or a passed unit test **does not prove** superior rendered thumbnails or better click-through rate.
- User-provided real photos should be preserved through original-pixel compositing; do not promise that a generative host preserves exact pixels without checking.
- The bundled reference atlas has **Bilibili and Xiaohongshu** content research; YouTube relies on platform principles/fallbacks, not an independently validated atlas.
- The bundled seven Xiaohongshu PNG examples are **abstract CSS layout mockups**, not real published covers. The 12 SVG previews are abstract original composition guides. No third-party cover screenshot library is shipped.
- Content, illustrations, game characters, branding, fonts and uploads must be used with appropriate rights. This **unofficial fan project** is not affiliated with or endorsed by Rockstar Games or Take-Two Interactive.

## Licensing / 授权状态

**No open-source license is selected in this beta package.** A public GitHub repository is not automatically open source. Please see [LICENSE_DECISION.md](LICENSE_DECISION.md). The owner should select an explicit license or usage permission before promising reuse, redistribution or commercial rights.

## Feedback / 反馈

For bugs and quality comparisons, open a GitHub Issue and attach the platform, topic, exact headline, host/tool environment and (if authorized) a before/after thumbnail pair. Avoid uploading private photos or confidential assets.
