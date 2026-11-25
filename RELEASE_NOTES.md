# GTA Thumbnail Pro v2.8.0-beta — Release Notes

## 中文｜首发 Beta

这是基于 **V2.8.0 视觉生成决策层重构**的首个 GitHub Beta 发布包，核心代码与规则不增加新功能，主要整理安装、文档、版权敏感素材和发布结构。

### 核心功能

- 创意导演优先：先组织画面故事、镜头和主体，再处理标题。
- 12 套视觉设计规则；根据内容匹配风格，也支持用户明确指定风格。
- A/B/C 三种独立设计思路，强调构图差异而非重复叠字幕。
- 标题的字阶、视觉主词和空间关系；保留原标题。
- WorkBuddy / Codex 等不同 AI 宿主使用同一真人原貌保护规则，实际生图与抠图取决于宿主工具。
- 三平台设计基础；YouTube 内容研究覆盖度低于 B站和小红书。

### 文件与使用

- `GTA_Thumbnail_Pro_v2.8.0-beta_Skill.zip`：解压到支持 Skills 的工作环境，保留完整目录。
- `GTA_Thumbnail_Pro_v2.8.0-beta_GitHub_Source.zip`：上传 GitHub 根目录的源码，不需要上传此 ZIP 本身。
- `tools/thumbnail-editor.html`：可在浏览器打开的离线编辑器。

**注意：** 本项目不附带图像生成模型、自动抠图模型或游戏素材。脚本测试仅验证规则/编译行为，尚不代表实际封面一定优于 AI 宿主原生生成；需要真实成品 A/B 对比。没有选择开源许可证，不能自动声称 MIT 或完全开源。

## English | First beta release

GTA Thumbnail Pro v2.8.0-beta packages the existing V2.8 visual decision refactor for an initial GitHub release **without introducing additional image-generation features**.

### Highlights

- **Visual creative direction first:** viewer hook, scene story, composition and spatial relationships precede typography.
- **Twelve visual design styles**, selected by content or explicit user preference.
- **Independent A/B/C concepts**, rather than one screenshot and different subtitle positions.
- **Editable title hierarchy** and exact preservation of user-provided text.
- **Real-photo protection**: uploaded real people must not be silently redrawn; alpha cutout and compositing are tool-dependent.
- **Bilibili, Xiaohongshu and YouTube** design basics, with disclosed uneven research coverage.

### Limitations

This is a Skill and offline editor, **not** a hosted AI image generator or an automatic segmentation system. The quality of rendered images depends on the host and requires visual comparison. The package intentionally excludes third-party reference thumbnails and private research screenshots. Licensing is not yet selected; this is a public beta, not automatically an open-source licensed release.

### Suggested feedback

Please share the host/tool, content topic, exact title, and a permission-safe native-vs-Skill image pair. Do not publish private portraits or unauthorized game assets.
