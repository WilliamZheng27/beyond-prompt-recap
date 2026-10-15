"""一分钟速看 + 制作过程 → 单文件 HTML（GitHub Pages 用）
代码原样取自演示文档 index.html：makeRecap / makeMakingOf 及其依赖的顶层函数（deps.py 算出）、第 32 页播放器 W['code-video-demo']；
9 张图片（时间线 8 张公开样图 + 广场舞照片）以 base64 内联。
用法：python3 build.py <演示文档目录> <deps.json> <输出 index.html>"""
import base64, html, json, re, sys

D, deps_json, out = sys.argv[1:4]
src = open(f'{D}/index.html', encoding='utf-8').read()
deps = json.load(open(deps_json, encoding='utf-8'))['text']


def one(s, a, b):
    c = s.count(a); assert c == 1, (c, a[:80]); return s.replace(a, b)


# ---------- 素材内联 ----------
ASSETS = [f'assets/tl-{k}.jpg' for k in ['gan', 'ddpm', 'sd', 'dit', 'controlnet', 'sora', 'flux', 'veo3']] + ['assets/square-dance.jpg']
asset_js = 'const ASSET = {\n' + ',\n'.join(
    f"  '{p}': 'data:image/jpeg;base64,{base64.b64encode(open(f'{D}/{p}', 'rb').read()).decode()}'" for p in ASSETS) + ',\n};'

# ---------- 依赖代码 ----------
code = '\n\n'.join(deps)
code = one(code, "const img = (src) => { const i = new Image(); i.src = src; return i; };",
           "const img = (src) => { const i = new Image(); i.src = ASSET[src] || src; return i; };")

# ---------- 播放器：第 32 页的 W['code-video-demo'] 原样搬过来 ----------
a = src.index("W['code-video-demo'] = {"); b = src.index('\n};\n', a) + 3
player = src[a:b].replace("W['code-video-demo'] = {", 'const App = {', 1)
player = one(player, 'this.MK = makeMakingOf(this.R, Deck.slides.map((x) => x.dataset.id), this.POSTER);',
             'this.MK = makeMakingOf(this.R, DECK_IDS, this.POSTER);')
player = one(player, '  // 制作过程：盖在整页上的第二块画布；只在第一次进入本页时自动播放，侧栏按钮可重播\n',
             '  // 制作过程：盖在整页上的第二块画布；侧栏「▶ 制作过程」点开\n')
paint_range = re.search(r'^const paintRange = .*$', src, re.M)[0]
speed_css = '\n'.join(l for l in src.split('\n') if 'mk-speed' in l and l.startswith(('.', '/*')))
speed_html = re.search(r'<div class="mk-speed" id="mkSpeed".*?</div>', src)[0]
ids = re.findall(r'<section class="slide[^"]*"[^>]*data-id="([^"]+)"', src)

# ---------- 页面 ----------
fonts = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/css2[^"]+)">', src)[1]
title = re.search(r'(<h2 class="title reveal">Demo: this talk in.*?</h2>)', src)[1].replace(' reveal', '')
a = src.index('<div class="rc-side reveal">', src.index('data-id="code-video-demo"')); b = src.index('</div>\n  </div>\n  <canvas class="mk"', a)
side = src[a:b + len('</div>\n')].replace(' reveal', '')
side = one(side, '<button class="rc-mk" id="mkReplay" data-en="↻ Making-of">↻ 制作过程</button>',
           '<button class="rc-mk" id="mkReplay" data-en="▶ Making-of" title="制作过程（M）">▶ 制作过程</button>')
a = src.index('<div class="rc-player reveal" id="rcPlayer">'); b = src.index('<div class="rc-side reveal">', a)
playerhtml = src[a:b].replace(' reveal', '').rstrip() + '\n'
playerhtml = one(playerhtml, 'title="铺满本页（Esc 退出）"', 'title="全屏（Esc 退出）"')

CREDIT_ZH = '时间线样图取自 GAN、DDPM、Stable Diffusion、DiT、ControlNet、FLUX 的论文 / 官方仓库，Sora、Veo 3 截帧来自 Wikimedia Commons（公有领域）；仅用于非商用分享'
CREDIT_EN = 'Timeline samples from the GAN, DDPM, Stable Diffusion, DiT, ControlNet and FLUX papers / official repos; Sora and Veo 3 frames from Wikimedia Commons (public domain). Non-commercial use only.'

CSS = r'''
:root {
  --stage-bg: #060708; --slide-bg: #0d0f12; --ink: #ece8df; --ink-2: #b9b5ab; --muted: #7d8492;
  --line: rgba(236, 232, 223, .10); --line-2: rgba(236, 232, 223, .20); --panel: #14171d; --panel-2: #1b1f27;
  --lime: #c8f03c; --orange: #ff7a45; --cyan: #5cc8ff;
  --f-serif: 'Fraunces', 'Noto Serif SC', 'Songti SC', serif; --f-serif-zh: 'Noto Serif SC', 'Songti SC', serif;
  --f-sans: 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', sans-serif; --f-mono: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
  --pad-x: 120px; --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: var(--stage-bg); }
/* 固定 1920×1080 舞台，整体等比缩放到窗口（同演示文档） */
.vp { position: fixed; inset: 0; overflow: hidden; background: var(--stage-bg); }
.stage { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }
.slide {
  position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden;
  font-family: var(--f-sans); color: var(--ink); padding: 150px var(--pad-x) 110px;
  background:
    radial-gradient(900px 600px at 100% 0%, rgba(200, 240, 60, .05), transparent 70%),
    radial-gradient(700px 500px at 0% 100%, rgba(92, 200, 255, .04), transparent 70%),
    linear-gradient(var(--line) 1px, transparent 1px) 0 0 / 80px 80px,
    linear-gradient(90deg, var(--line) 1px, transparent 1px) 0 0 / 80px 80px,
    var(--slide-bg);
  background-blend-mode: normal, normal, soft-light, soft-light, normal;
}
.chrome { position: absolute; top: 56px; left: var(--pad-x); right: var(--pad-x); display: flex; justify-content: space-between;
  font: 500 18px/1 var(--f-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.chrome .sec { color: var(--lime); }
.chrome .r { position: relative; padding-right: 128px; }
.lang-sw { position: absolute; right: 0; top: 50%; transform: translateY(-50%); display: flex; padding: 3px;
  border: 1.5px solid var(--line-2); border-radius: 999px; background: rgba(13, 15, 18, .6); letter-spacing: 0; text-transform: none; }
.lang-sw button { font: 600 16px/1 var(--f-mono); color: var(--muted); background: none; border: 0; border-radius: 999px; padding: 7px 14px; cursor: pointer; transition: background .25s, color .25s; }
.lang-sw button:hover { color: var(--ink); }
html:not(.lang-en) .lang-sw [data-lang="zh"], html.lang-en .lang-sw [data-lang="en"] { background: var(--lime); color: #0d0f12; }
h2 { font-family: var(--f-serif); font-weight: 900; letter-spacing: -.01em; }
h2.title { font-size: 68px; line-height: 1.18; margin-bottom: 22px; transition: opacity .55s var(--ease), transform .7s var(--ease); }
h2.title em { font-style: normal; color: var(--lime); }
.zh { display: block; font-family: var(--f-serif-zh); font-weight: 600; color: var(--ink-2); letter-spacing: 0; font-style: normal; }
h2.title .zh { font-size: 34px; line-height: 1.4; margin-top: 12px; }
.rng { -webkit-appearance: none; appearance: none; height: 6px; border-radius: 3px; outline: none; cursor: pointer;
  background: linear-gradient(90deg, var(--lime) var(--p, 0%), var(--line-2) var(--p, 0%)); }
.rng::-webkit-slider-thumb { -webkit-appearance: none; width: 28px; height: 28px; border-radius: 50%; background: var(--ink); border: 5px solid var(--lime); box-shadow: 0 0 0 7px rgba(200, 240, 60, .15); }
.rng::-moz-range-thumb { width: 18px; height: 18px; border-radius: 50%; background: var(--ink); border: 5px solid var(--lime); }
.rc { display: grid; grid-template-columns: 1168px 1fr; gap: 40px; margin-top: 26px; }
.rc-player { position: relative; width: 1168px; height: 657px; border-radius: 10px; overflow: hidden; background: #08090b; box-shadow: 0 0 0 1px var(--line-2), 0 30px 80px rgba(0, 0, 0, .45); }
.rc-player canvas { display: block; width: 100%; height: 100%; cursor: pointer; }
.rc-big { position: absolute; right: 70px; bottom: 120px; display: flex; align-items: center; gap: 14px; padding: 16px 28px 16px 22px; border: 0; border-radius: 40px;
  background: var(--lime); color: #0d0f12; font: 700 24px var(--f-sans); cursor: pointer; box-shadow: 0 10px 40px rgba(200, 240, 60, .3); transition: transform .2s; }
.rc-big i { font-style: normal; font-size: 28px; }
.rc-big small { font: 500 17px var(--f-mono); opacity: .7; }
.rc-big:hover { transform: scale(1.05); }
.rc-bar { position: absolute; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 14px; padding: 44px 20px 14px; background: linear-gradient(transparent, rgba(8, 9, 11, .88)); transition: opacity .3s; }
.rc-bar button { font: 600 18px var(--f-mono); color: var(--ink); background: rgba(13, 15, 18, .5); border: 1.5px solid var(--line-2); border-radius: 6px; height: 40px; min-width: 48px; padding: 0 10px; cursor: pointer; }
.rc-bar button:hover { border-color: var(--lime); color: var(--lime); }
.rc-bar button.off { color: var(--muted); text-decoration: line-through; }
.rc-bar .rng { flex: 1; }
.rc-bar b { font: 500 17px var(--f-mono); color: var(--ink-2); min-width: 150px; text-align: center; }
.rc-player.on .rc-big { display: none; }
.rc-player.playing .rc-bar { opacity: 0; }
.rc-player.playing:hover .rc-bar { opacity: 1; }
.rc-player.full { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; border-radius: 0; z-index: 40; transform: none !important; box-shadow: none; }
.rc-player.rec::after { content: '● REC'; position: absolute; top: 14px; left: 50%; transform: translateX(-50%); font: 600 16px var(--f-mono); color: #ff5c5c; background: rgba(8, 9, 11, .75); padding: 4px 12px; border-radius: 4px; }
.rc-side { display: flex; flex-direction: column; gap: 14px; transition: opacity .55s var(--ease), transform .7s var(--ease); }
.rc-it { background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--lime); border-radius: 6px; padding: 14px 20px 16px; }
.rc-it b { display: block; font: 600 15px var(--f-mono); color: var(--lime); letter-spacing: .08em; margin-bottom: 6px; }
.rc-it p { margin: 0; font-size: 19px; line-height: 1.5; color: var(--ink-2); }
.rc-it code { font: 500 17px var(--f-mono); color: var(--ink); }
.rc-it.o { border-left-color: var(--orange); }
.rc-it.o b { color: var(--orange); }
.rc-n { margin-top: auto; display: flex; align-items: baseline; gap: 14px; color: var(--muted); font-size: 18px; }
.rc-n b { font: 900 60px var(--f-serif); color: var(--ink); }
.rc-n span, .rc-mk { white-space: nowrap; }
.rc-mk { margin-left: auto; font: 600 16px var(--f-mono); color: var(--ink-2); background: none; border: 1.5px solid var(--line-2); border-radius: 6px; padding: 8px 14px; cursor: pointer; }
.rc-mk:hover { color: var(--lime); border-color: var(--lime); }
.mk { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; z-index: 30; display: none; }
.mk-skip { position: absolute; right: 120px; bottom: 40px; z-index: 31; display: none; font: 600 18px var(--f-mono); color: var(--ink-2); background: rgba(13, 15, 18, .6); border: 1.5px solid var(--line-2); border-radius: 6px; padding: 10px 18px; cursor: pointer; }
.mk-skip:hover { color: var(--lime); border-color: var(--lime); }
.slide.mk-on .mk, .slide.mk-on .mk-skip { display: block; }
.slide.mk-on:not(.mk-hide) .mk-skip { display: none; }
.slide.mk-hide .title, .slide.mk-hide .rc-side, .slide.mk-hide .foot { opacity: 0 !important; transform: translateY(26px) !important; }
.slide.mk-hold .rc-player { opacity: 0 !important; transition: none !important; }
.rc-player.pop { animation: rcPop .6s cubic-bezier(.34, 1.56, .64, 1); }
.rc-player.pop .rc-big { animation: rcBig .55s cubic-bezier(.34, 1.56, .64, 1) .2s both; }
@keyframes rcPop { from { transform: scale(.985); } to { transform: scale(1); } }
@keyframes rcBig { from { transform: scale(0); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.foot { position: absolute; left: var(--pad-x); right: var(--pad-x); bottom: 26px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font: 400 14px/1.5 var(--f-mono); color: var(--muted); transition: opacity .55s var(--ease), transform .7s var(--ease); }
{speed_css}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .2s !important; } }
'''.replace('{speed_css}', speed_css)

APP = r'''
/* ---------- 单页外壳：舞台缩放、中英切换、键盘、浏览器全屏 ---------- */
const stage = $('#stage'), slide = $('#slide');
const fit = () => {
  const k = Math.min(innerWidth / 1920, innerHeight / 1080);
  stage.style.transform = `translate(${(innerWidth - 1920 * k) / 2}px, ${(innerHeight - 1080 * k) / 2}px) scale(${k})`;
};
addEventListener('resize', fit); fit();
// 双语：data-en 里是英文 HTML，中文原文存进 data-zh，切换时整段替换
document.querySelectorAll('[data-en]').forEach((el) => { el.dataset.zh = el.innerHTML; });
const applyLang = () => {
  document.querySelectorAll('[data-en]').forEach((el) => { el.innerHTML = Lang.en ? el.dataset.en : el.dataset.zh; });
  document.documentElement.lang = Lang.en ? 'en' : 'zh-CN';
};
document.addEventListener('langchange', applyLang);
Lang.init(); applyLang();
App.init(slide);
// ⛶：播放器铺满舞台，同时让浏览器进入全屏；退出全屏（Esc）时一起还原
const full0 = App.full.bind(App);
App.full = (on) => {
  full0(on);
  if (on && !document.fullscreenElement && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {});
  if (!on && document.fullscreenElement) document.exitFullscreen().catch(() => {});
};
document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement) full0(false); });
addEventListener('keydown', (e) => {
  if (e.target.closest && e.target.closest('input')) return;
  if (e.key === ' ' && !App.mkRaf) { e.preventDefault(); App.playing ? App.pause() : App.play(); }
  else if (e.key === 'l' || e.key === 'L') Lang.toggle();
  else if (e.key === 'm' || e.key === 'M') App.making();
});
'''

page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Beyond Prompt · 一分钟速看</title>
<meta name="description" content="一场 AIGC 可控生成技术分享的 60 秒速看：画面 render(g, t) 和音乐（Web Audio 实时合成）全部由 Claude 写的 JS 生成，附制作过程动画。">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230d0f12'/%3E%3Cpath d='M12 9l12 7-12 7z' fill='%23c8f03c'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{html.escape(fonts)}">
<style>{CSS}</style>
</head>
<body>
<!--
  Beyond Prompt · 一分钟速看（单文件版）
  画面：makeRecap().render(g, t) 纯函数逐帧绘制；音乐：同一个乐谱 score() + Web Audio 合成器 synth() 实时合成。
  制作过程：makeMakingOf() 用同一份源码、镜头关键帧和乐谱画出“需求 → 分镜 → 写代码 → 镜头 → 配乐 → 自检 → 成片”（约 33 秒，0.5×–2× 可调速）。
  代码原样取自演示文档（2026-10-14 AIGC 技术分享），9 张图片以 base64 内联。快捷键：空格 播放 / 暂停 · M 制作过程 · L 中 / EN · Esc 跳过 / 退出全屏。
-->
<div class="vp"><div class="stage" id="stage">
<section class="slide" id="slide">
  <div class="chrome"><span>AIGC · Beyond Prompt</span><span class="r"><span class="sec">+ Code → Video</span><span class="lang-sw"><button data-lang="zh">中</button><button data-lang="en">EN</button></span></span></div>
  {title}
  <div class="rc">
    {playerhtml}    {side}  </div>
  <canvas class="mk" id="mkCanvas" width="1920" height="1080"></canvas>
  <button data-en="Skip ›" class="mk-skip" id="mkSkip">跳过 ›</button>
  {speed_html}
  <div class="foot" data-en="{html.escape(CREDIT_EN)}">{html.escape(CREDIT_ZH)}</div>
</section>
</div></div>
<script>
{asset_js}

// 演示文档 {len(ids)} 页的 id（制作过程里“通读 N 页演示”用）
const DECK_IDS = {json.dumps(ids)};

{paint_range}

{code}

{player}
{APP}
</script>
</body>
</html>
'''
open(out, 'w', encoding='utf-8').write(page)
print(out, len(page.encode()) // 1024, 'KB', len(ids), 'slides')
