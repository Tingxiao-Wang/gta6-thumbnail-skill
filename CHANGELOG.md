# Changelog / 更新日志

## v2.8.0-beta — First GitHub beta release / GitHub 首发 Beta

- Packaging and documentation release based on the tested V2.8.0 decision-refactor source. **No new image-generation features** are claimed.
- Published clean bilingual README, install guide, release notes, manual comparison instructions, and source/install archives.
- Removed obsolete generated `examples/compiled_*`, historical directive files, and outdated validators; retained current V2.8 runtime and regression tests.
- Confirmed embedded third-party research screenshots and the former 29-image reference bank are **not** shipped.
- Preserved privacy-safe real-person photo handling. Actual image generation, subject extraction and text rendering remain host-dependent.
- No license chosen or added. See `LICENSE_DECISION.md` before explicitly describing the repository as open-source.

---

## V2.8.0-test — Visual Creative Director Refactor / 视觉生成决策层重构

- Added `scripts/creative_director_v28.py`: visual-story question → whole-scene composition → meaningful non-textual changes → lossless title hierarchy → production prompt.
- Three independent A/B/C visual architectures; narrative-story analysis is routed to S01/S05/S06 rather than unsupported map-style visuals.
- Removed old fixed V2.4.1 title coordinate contract and conflicting long Fxx prompts from final `prompt-A/B/C.txt`; offline editor title blocks now use V2.8 planned coordinates.
- Replaced the layered, contradictory legacy Doubao instruction file with a compact V2.8 authority; archived historic originals in docs/.
- Added an explicit paired benchmark protocol for *real rendered images*. No claim of improved quality without user-host trials.
- Preserves V2.5.2 intake gate, V2.7 twelve style definitions, V2.7.1 font effects, V2.7.2 non-regeneration guard, YouTube fallback, no fabricated facts.

## V2.7.2 — Real Person Photo Preservation Guard / 真人原图保护测试版
- Highest-priority no-regeneration default for user-uploaded real-person photos. Role confirmation alone does not grant consent to generate altered likenesses.
- Propagate `asset_kind=real_person_photo` through intake metadata; standalone protection policy emitted by handoff and legacy compiler.
- All A/B/C image prompts explicitly require reusing original person pixels via non-generative compositing; style/title systems cannot override.
- Scoped, explicit `person_regeneration_approval` required for specified image edits; generic styling is not approval.
- QA veto added for unauthorized re-generation; no promise of preservation when the host can only regenerate whole images.

## V2.7.1 · Title Visual Impact Preview
- Added 12 title impact profiles in `references/title_impact_v271.json`.
- Added exact-text/keyword title hierarchy planner in `scripts/title_impact_v271.py`, wired into all A/B/C visual prompts and handoff.
- Added style-aware editable headline-block size, rotation, outline settings to offline brief compiler.
- Added reversible title impact controls to offline editor (style + subtle / strong / bold).
- Protected purposeful bold title effects from generic de-AI clamping, while keeping no-text style and factual integrity.
- No image generation model is bundled. Output quality remains to be validated in the target AI host.

# V2.6.1 — Visual Diversity / 视觉画面丰富度

- Add distinct scene-level A/B/C plans for the 15 content cases (Bilibili 8 + Xiaohongshu 7), YouTube fallback.
- Preserve all intake and role-confirmation gates, existing HTML atlas and typography editor.
- Move functional circles/arrows/zoom windows/comparison cards from blanket decoration avoidance into evidence-based decisions.
- Handoff emits `visual_variants[]`; local script emits `visual-prompt-A/B/C.txt`.
- Mark fast mode vs independent-scene mode explicitly to avoid falsely claiming visual diversity on one shared background.
- No third-party reference images are bundled in this GitHub candidate.

# V2.6 Preview · 2026-11-23

- Replaced fixed 29-image reference library and manifest with a user-provided HTML content atlas.
- 8 Bilibili content categories, 7 Xiaohongshu categories, 32 private local research screenshots, 7 CSS design mockups.
- Explicitly marks YouTube as uncovered and uses old platform design fallback.
- Rewired the selection and generation-handoff scripts to the content atlas.
- Preserves strict intake/question flow and separated user subject vs style reference logic.
- Removed old third-party bundled reference images in both trial and public-safe builds.
- Public-safe build strips all embedded third-party research screenshots from manual HTML and content atlas assets.

## V2.7 Design System Test（2026-11-24）
- Integrated user-provided `GTA6封面设计原则_V1.0.html` as the primary 12-style design system.
- Added 12 distinct style JSON files and 12 original abstract SVG previews; no third-party research thumbnails added.
- Added platform parameters, 14 content-to-style mappings, three creative levels and grounded quality-review rubric.
- A/B/C can use three distinct auto-matched visual styles; explicit style locks one visual language across three different scene directions.
- Deactivated legacy hard-coded default magenta grading in the V2.7 compiler; styles control their own palette.
- Bridged current atlas handoff and legacy offline compiler; the compiler now requires confirmed intake state.
- Quality review remains pending until real rendered images are inspected; HTML editor is unchanged.
