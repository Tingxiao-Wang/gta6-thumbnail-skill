# Installation / 安装说明 · v2.8.0-beta

**The Skill is a folder with a root `SKILL.md`, not a single prompt string.**
**这是带有 `SKILL.md` 入口和完整依赖目录的 Skill，不是一段提示词。**

## Install in WorkBuddy / WorkBuddy 安装

1. Download the Skill ZIP from the GitHub release, extract it as `gta-thumbnail-pro/`.
2. In a WorkBuddy workspace that supports custom Skills, use its Skills import/install flow to point at this folder or its root `SKILL.md`. The exact UI and permission model depend on your installed WorkBuddy version.
3. Do not import only `SKILL.md`; the `scripts/`, `styles/`, `references/`, and `tools/` directories are needed.
4. Test with the title in `README.md`. Check whether the host can actually read uploaded images and call its image-generation/image-editing features.

## Install in Codex / Codex 安装

1. Extract the Skill ZIP, keeping the complete `gta-thumbnail-pro/` folder.
2. Copy/install it into the custom-Skill location supported by your Codex runtime, or add it to a Skills-enabled workspace following that runtime's local settings. Do not assume every Codex environment has identical skill discovery or image tools.
3. Ensure the runtime reads the **current root `SKILL.md`** and is not loading older V2.7 instruction files.
4. When using a real self-portrait, verify the host can perform **non-generative alpha-mask cutout** before compositing. If it cannot, report this limitation and do not regenerate the person's appearance or silently substitute a rectangular picture-in-picture.

## Other compatible hosts / 其他兼容环境

If the host can read Skill folders but cannot run Python, the design rules may still inform prompts. The bundled Python commands are optional offline tooling, not an image model. Some host features may be unavailable.

## Offline compiler / 本地编译测试

Requires Python 3; no third-party Python dependency is required for the included rule/compiler smoke test.

```bash
python tests/test_v28.py
python tests/test_v272_person_photo.py
python tests/test_v252_intake.py
python tools/compile_brief.py --brief examples/v28_story_retest/input.json --out output-v28
```

The compiler writes A/B/C prompts and offline editor JSON, **not finished AI images**. The input sample is a hypothetical topic; don't treat generated concept art as genuine game evidence.

## How to identify correct behavior / 正常行为检查

- Before processing uploads, the agent determines whether each is a subject, style reference, both, or excluded.
- For an unspecified style, A/B/C can use different visual concepts; for an explicitly specified style, they retain that style's core traits.
- Do not treat adding one subtitle to the same screenshot as a successful three-variation design.
- The user's exact title text must remain intact; don't invent scores, dates, announcements or story facts.
- Without explicit permission, a real uploaded person's appearance is not regenerated.

## Troubleshooting / 常见问题

- **Only one subtitle line? / 只有一行字幕：** Verify the final prompt came from the V2.8 `creative_director_v28.py` pipeline, not old fixed-title templates.
- **No image output? / 没有出图：** Check whether the host provides and authorizes an image-generation or editing tool. Python scripts here only plan and compile.
- **Portrait turns into a lookalike? / 真人被重绘：** Stop and switch to original-pixel compositing, or explain tool limits.
- **A/B/C identical? / 三图相似：** Ask the host to render the independent visual variants separately and compare scene composition, not just fonts.
