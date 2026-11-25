# 🎮 GTA Thumbnail Pro

### Design the thumbnail. Don't just add text.

**一款让 AI 真正参与视频封面设计，而不只是给图片添加字幕的 GTA6 专用 Skill。**

A content-driven GTA 6 thumbnail design Skill for **Bilibili, YouTube and Xiaohongshu**.

**Version:** `v2.8.0-beta` · Public Beta

---

## 01 / 为什么开发这个 Skill？

使用 AI 制作视频封面时，我们经常遇到这样的问题：

- 图片很好看，但更像游戏截图，而不是视频封面。
- 标题很大，却缺少字体设计、信息层级和视觉节奏。
- 人物、场景和文字各自独立，缺少整体构图。
- 不同提示词生成的结果越来越相似。
- 上传真人照片后，人物形象可能被 AI 擅自重新绘制。

GTA Thumbnail Pro 希望解决的不是单纯的生图问题，而是**让 AI 学会从内容出发，做出更有视觉表现力的封面设计决策。**

## 02 / 同样的提示词，为什么效果不同？

以下两张封面使用 WorkBuddy，在相同图片素材与相同文本需求下进行生成。

**测试提示词：**

> 我要制作 GTA6 游戏的视频封面，标题是「是游戏？还是壁纸模拟器？」

| WorkBuddy 原生生成 | WorkBuddy + GTA Thumbnail Pro |
|---|---|
| ![Without Skill](assets/showcase/without-skill.png) | ![With Skill](assets/showcase/with-skill.png) |
| 未加载 Skill | 
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b5dc7397-a595-4b63-89a9-e101e29d0f59" />

| 加载 GTA Thumbnail Pro |
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7622ffa4-4938-4ddc-b569-6578bc099521" />


| 以游戏截图为主要背景，叠加标题和人物 | 重新组织文字、人物和游戏场景，形成更明确的视觉结构 |

### 这组案例体现了什么？

**① 从添加标题，到设计标题**

原生版本将主要文字集中在画面区域中，强调字号和描边。

Skill 版本则将「是游戏？」与「还是壁纸模拟器？」划分成两组不同视觉权重的信息，通过字号、色彩和排列强化阅读节奏。

**② 从简单拼贴，到有层次的构图**

Skill 版本重新组织了真人主体、游戏场景和文字的位置关系，形成更明确的左右分区。

标题负责传递核心问题，游戏场景提供内容依据，真人主体承担情绪表达。

**③ 从单一画面，到完整的封面信息结构**

Skill 不只考虑背景和标题，还会根据内容需要安排辅助标签、次级信息、视觉引导和留白。

它的目标不是增加无意义装饰，而是让每个元素都承担明确的表达功能。

> **说明：** 以上是一次真实工作流的定性对照，不代表 Skill 在所有任务中必然优于原生生成，也不代表已验证点击率提升。生成效果仍受宿主模型、图片工具及输入素材影响。

---

## 03 / 核心功能 Features

### 🎨 12 种独立视觉设计风格

不只是切换滤镜和背景颜色，而是为不同类型的视频提供不同的画面组织方法。

| 风格 | 设计方向 | 适用内容 |
|---|---|---|
| S01 电影叙事 | 人物关系、环境纵深、光影叙事 | 剧情、角色、实况 |
| S02 悬念探索 | 局部特写、目标聚焦、视觉引导 | 彩蛋、隐藏细节 |
| S03 强反差对比 | 双画面、冷暖反差、视觉冲突 | 画质、新旧版本 |
| S04 超大数字 | 真实数字主导视觉 | 测评、数据、挑战 |
| S05 多图拼贴 | 主次图片、档案与信息组织 | 解析、盘点 |
| S06 背景巨字 | 文字与人物产生前后遮挡 | 角色、观点 |
| S07 荒诞名场面 | 动作瞬间、情绪冲击 | 搞笑、整活 |
| S08 快讯爆料 | 核心消息、资讯版式 | 新闻、更新 |
| S09 地图攻略 | 地图、定位和任务信息 | 攻略、收集 |
| S10 复古杂志 | 印刷质感、编辑式排版 | 城市、文化 |
| S11 原生奇观 | 保留真实画面的传播力 | 高能瞬间、游戏实况 |
| S12 极简氛围 | 留白、色彩与环境情绪 | 摄影、壁纸 |

### 🧠 内容驱动的创意导演

在生成封面之前，Skill 会优先分析：

1. 视频核心内容是什么？
2. 观众为什么会点击？
3. 什么视觉画面最能表现这个看点？
4. 主体、背景和标题应该如何组织？

设计流程：

**理解内容 → 形成视觉概念 → 组织画面 → 设计标题 → 生成方案 → 审核结果**

### 🅰️ A/B/C 三套独立创意

默认生成三种不同的整体设计方向，而不只是更换字体和标题位置。

例如，剧情解析类视频可以采用电影人物叙事、剧情信息拼贴或背景巨字构图。

用户指定某一种风格时，Skill 会优先保留该风格的核心视觉特征，在同一风格中探索不同方案。

### 🔠 更有视觉冲击力的标题

支持关键词强调、多级文字层次、粗描边、立体阴影、文字倾斜、背景巨字等设计思路。

文字设计会根据封面风格变化，而不是让所有封面使用同一种夸张发光字。

### 📷 真人原貌保护

上传真实本人照片时，默认不允许 AI 擅自重新生成人物形象。

在工具能力允许的情况下，可以使用非生成式抠图、原图裁切、缩放和图层合成。未经用户明确要求，不应重新绘制脸部、发型、身形、服饰或表情。

**注意：** Skill 不能让不支持原像素合成的生图工具自动获得这项能力。

### 🖥️ 三平台适配

支持按 B站、YouTube 和小红书的封面尺寸、阅读习惯及画面安全区规划设计。

项目包含 B站与小红书内容类型参考；YouTube 目前以平台设计原则和风格规则为主。

---

## 04 / 如何安装？

### 方法一：下载 GitHub 仓库

1. 打开本项目 GitHub 页面。
2. 点击 **Code → Download ZIP**。
3. 解压项目。
4. 在支持自定义 Skill 的 AI 环境中加载项目根目录下的 `SKILL.md`，并保留全部配套文件夹。

### 方法二：安装独立 Skill 包

发布 Release 后，可从 Releases 页面下载独立 Skill ZIP，并按使用平台的安装方式导入。

详细说明请查看 [INSTALL.md](INSTALL.md)。

### 运行环境

本项目是 AI 工作流 Skill，**不是独立的 AI 生图模型**。

WorkBuddy、Codex、豆包等环境对图片输入、图像编辑、真人抠图及文件操作的支持情况可能不同。最终功能以实际宿主工具权限为准。

---

## 05 / 如何使用？

你可以直接尝试：

```text
我要制作一张 B站 GTA6 视频封面。

视频主题：是游戏？还是壁纸模拟器？

我会提供游戏场景图片和真人照片。

请使用 GTA Thumbnail Pro：
1. 识别图片素材用途。
2. 分析视频的核心点击动机。
3. 构思 A/B/C 三种不同的完整视觉方案。
4. 强化标题的视觉冲击力。
5. 保留真人原貌，不擅自重新生成人物。
6. 使用可用的图像工具生成封面。
```

你也可以直接指定 S01–S12 中的任一种视觉风格，或者上传自己喜欢的封面作为风格参考。

---

## 06 / 项目结构

```text
gta6-thumbnail-skill/
├── SKILL.md
├── README.md
├── INSTALL.md
├── RELEASE_NOTES.md
├── scripts/
├── styles/
├── references/
├── assets/
├── tools/
│   └── thumbnail-editor.html
├── tests/
└── examples/
```

项目还提供离线 HTML 编辑器，用于进一步调整文字和导出封面。编辑器本身不包含独立生图模型或自动人像分割引擎。

## 07 / 已知限制

- AI 生成结果存在随机性，不保证每次都获得最佳视觉效果。
- A/B/C 是否成功生成三张独立图片，取决于宿主工具是否实际执行各自任务。
- 文字渲染准确性仍可能受生成模型影响。
- 真人原像素保护需要合适的图层处理工具。
- 尚未进行大规模、可复现的点击率 A/B 测试。
- 使用游戏素材、个人照片和第三方字体时，请确认相关使用权限。

## 08 / English Introduction

**GTA Thumbnail Pro** is a content-driven AI thumbnail design workflow built for GTA 6 creators on Bilibili, YouTube and Xiaohongshu.

Instead of simply placing large text over a screenshot, it helps compatible AI environments plan a visual story, organize the composition, establish information hierarchy, and develop distinctive thumbnail concepts.

**Highlights:**

- 12 independent visual design styles
- Content-first creative direction
- Three distinct A/B/C thumbnail concepts
- Advanced typography and headline emphasis
- Real-person appearance protection
- Platform-aware composition and export guidance
- Offline HTML layout editor

The included test comparison illustrates how the Skill can change a generated thumbnail's layout and visual hierarchy. It is not proof of consistent quality improvements or higher click-through rates.

The Skill relies on the connected AI host for image generation, image editing and background removal.

## 09 / Feedback & Contributions

欢迎反馈实际生成结果，尤其是相同素材、相同提示词下，启用与不启用 Skill 的对照案例。

You can submit feedback through [GitHub Issues](https://github.com/Tingxiao-Wang/gta6-thumbnail-skill/issues).

## License & Disclaimer

This beta does not yet include a selected open-source license. Public availability does not automatically grant redistribution or commercial-use rights.

GTA Thumbnail Pro is an unofficial fan-made project. It is not affiliated with, sponsored by or endorsed by Rockstar Games or Take-Two Interactive.

---

**GTA Thumbnail Pro — From content to visual storytelling.**

**不止生成一张图，而是让 AI 真正参与封面设计。**
