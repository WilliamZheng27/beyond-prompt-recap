# Beyond Prompt · 一分钟速看

2026-10-14 AIGC 技术分享《Beyond Prompt：可控生成的现状》的 60 秒速看，以及 23 秒的制作过程动画。

**在线观看：** https://williamzheng27.github.io/beyond-prompt-recap/

- 画面：`makeRecap().render(g, t)` 是纯函数，每帧在 1920×1080 的 canvas 上实时绘制，整片是一张 8800×3640 的大画布，镜头沿关键帧一镜到底。
- 音乐：同一份乐谱 `score()`（120 BPM，C–G–Am–F，1311 个音符事件）由 Web Audio 振荡器和噪声实时合成，没有音频文件。
- 制作过程：`makeMakingOf()` 用同一份源码、镜头表和乐谱画出“需求 → 分镜 → 写代码 → 镜头 → 配乐 → 自检 → 成片”。
- 全部代码由 Claude 编写；`index.html` 是单文件，9 张图片以 base64 内联，只依赖 Google Fonts。

快捷键：空格 播放 / 暂停 · M 制作过程 · L 中 / EN · Esc 跳过 / 退出全屏。

## 素材

时间线样图取自 GAN（arXiv 1406.2661）、[DDPM](https://github.com/hojonathanho/diffusion)、[Stable Diffusion](https://github.com/CompVis/stable-diffusion)、[DiT](https://github.com/facebookresearch/DiT)、[ControlNet](https://github.com/lllyasviel/ControlNet)、[FLUX](https://github.com/black-forest-labs/flux) 的论文 / 官方仓库；Sora、Veo 3 截帧来自 Wikimedia Commons（公有领域）。仅用于非商用分享。

## 重新生成

`build/` 里是从演示文档导出单文件的脚本：

```bash
python3 build/deps.py <演示文档>/index.html deps.json
python3 build/build.py <演示文档目录> deps.json index.html
```
