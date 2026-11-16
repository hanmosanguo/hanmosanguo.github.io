#!/usr/bin/env python3
"""官網素材建置：從遊戲素材切出 S 向動畫條、壓截圖、主視覺、開場影片、字型子集。
用法（需要 Pillow、fonttools、brotli、ffmpeg）：python3 website/tools/build_assets.py
輸出到 website/assets/。只讀 huangjin_assets/、docs/appstore/、i18n/、steam/third_party 的字型。"""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
W = ROOT / 'website'
HA = ROOT / 'huangjin_assets'
OUT = W / 'assets'

# id: (sheet, cell_w, cell_h, row)
SPRITES = {
  'skeleton': ('enemies/sheets/skeleton_mob_walk_4dir_6f.png', 128, 160, 0),
  'refugee': ('enemies/sheets/refugee_mob_walk_4dir_6f.png', 128, 160, 0),
  'swordsman': ('enemies/sheets/yellow_turban_swordsman_walk_4dir_6f.png', 128, 160, 0),
  'swordsman_red': ('enemies/sheets/yellow_turban_swordsman_red_walk_4dir_6f.png', 128, 160, 0),
  'swordsman_silver': ('enemies/sheets/yellow_turban_swordsman_silver_walk_4dir_6f.png', 128, 160, 0),
  'swordsman_gold': ('enemies/sheets/yellow_turban_swordsman_gold_walk_4dir_6f.png', 128, 160, 0),
  'archer_red': ('enemies/sheets/yellow_turban_archer_red_walk_4dir_6f.png', 128, 160, 0),
  'archer_silver': ('enemies/sheets/yellow_turban_archer_silver_walk_4dir_6f.png', 128, 160, 0),
  'archer_gold': ('enemies/sheets/yellow_turban_archer_gold_walk_4dir_6f.png', 128, 160, 0),
  'cavalry_silver': ('enemies/sheets/yellow_turban_cavalry_silver_walk_4dir_6f.png', 128, 160, 3),
  'cavalry_gold': ('enemies/sheets/yellow_turban_cavalry_gold_walk_4dir_6f.png', 128, 160, 3),
  'shield': ('enemies/sheets/yellow_turban_shield_walk_4dir_6f.png', 128, 160, 0),
  'chain': ('enemies/sheets/yellow_turban_chain_walk_4dir_6f.png', 128, 160, 0),
  'armored': ('enemies/sheets/yellow_turban_armored_blade_walk_4dir_6f.png', 128, 160, 0),
  'sorcerer': ('enemies/sheets/yellow_turban_sorcerer_walk_4dir_6f.png', 128, 160, 0),
  'guan_yu': ('guan_yu/walk/guan_yu_walk_S_spritesheet.png', 128, 160, 0),
  'zhao_yun': ('zhao_yun/walk/zhao_yun_walk_S_spritesheet.png', 128, 160, 0),
  'deng_mao': ('bosses/deng_mao_v4/animations/walk/walk_4dir.png', 256, 320, 0),
  'gao_sheng': ('bosses/gao_sheng/animations/idle/idle_4dir.png', 256, 320, 0),
  'zhang_liang': ('bosses/zhang_liang_v3/animations/idle/idle_4dir.png', 256, 320, 0),
  'zhang_bao': ('bosses/zhang_bao/animations/idle/idle_4dir.png', 256, 320, 0),
  'zhang_jiao': ('bosses/zhang_jiao/animations/idle/idle_4dir.png', 256, 320, 0),
  'hei_hu_zang': ('bosses/hei_hu_zang/animations/idle/idle_4dir.png', 256, 320, 0),
}

def sprites():
  meta = {}
  d = OUT / 'sprites'; d.mkdir(parents=True, exist_ok=True)
  for sid, (p, cw, ch, row) in SPRITES.items():
    im = Image.open(HA / p).convert('RGBA')
    n = im.width // cw
    frames = [im.crop((i * cw, row * ch, (i + 1) * cw, (row + 1) * ch)) for i in range(n)]
    frames = [f for f in frames if f.getbbox()]
    bb = None
    for f in frames:
      b = f.getbbox()
      bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = bb
    x0 = max(0, x0 - 2); y0 = max(0, y0 - 2); x1 = min(cw, x1 + 2); y1 = min(ch, y1 + 2)
    fw, fh = x1 - x0, y1 - y0
    strip = Image.new('RGBA', (fw * len(frames), fh))
    for i, f in enumerate(frames):
      strip.paste(f.crop((x0, y0, x1, y1)), (i * fw, 0))
    strip.save(d / f'{sid}.webp', lossless=True, quality=100, method=6)
    meta[sid] = {'w': fw, 'h': fh, 'n': len(frames)}
    print(sid, fw, fh, len(frames))
  (OUT / 'sprites' / 'sprites.json').write_text(json.dumps(meta, indent=1))
  # favicon：關羽第一格頭部
  g = Image.open(OUT / 'sprites' / 'guan_yu.webp').convert('RGBA').crop((0, 0, meta['guan_yu']['w'], meta['guan_yu']['w']))
  for s, name in ((32, 'favicon-32.png'), (180, 'apple-touch-icon.png')):
    bg = Image.new('RGBA', g.size, (20, 14, 10, 255)); bg.alpha_composite(g)
    bg.resize((s, s), Image.NEAREST).save(OUT / 'img' / name)

ICONS = {  # 遊戲 HUD 實際使用的圖示（play.js ICON_PATH）
  'feilong': 'hud/skill_icons_v2/feilong_64.png', 'kanglong': 'hud/skill_icons_v2/kanglong_64.png',
  'jianlong': '_comfy_candidates/_finished_preview/icons_skills_a/jianlong_s41000_64.png', 'weizhen': 'hud/skill_icons_v2/weizhen_64.png',
  'shuiyan': '_comfy_candidates/_finished_preview/icons_skills_a2/shuiyan_s43000_64.png',
  'lihua': 'zhao_yun/skill_icons/lihua_64px.png', 'qijin': 'zhao_yun/skill_icons/qijin_64px.png', 'fengming': 'zhao_yun/skill_icons/fengming_64px.png',
  'manqiang': 'zhao_yun/skill_icons/manqiang_64px.png', 'shenglong': 'zhao_yun/skill_icons/shenglong_64px.png', 'buwude': 'zhao_yun/skill_icons/buwude_64px.png',
  'camp_infantry': 'camps_buildings/icons/infantry/camp_infantry_128px.png', 'camp_cavalry': 'camps_buildings/icons/cavalry/camp_cavalry_128px.png',
  'camp_archer': 'camps_buildings/icons/archer/camp_archer_128px.png',
  'qinglong': '_comfy_candidates/icons_p410/qinglong_blade/icon_64.png', 'longdan': '_comfy_candidates/_finished_preview/icons_divine_weapons_1/longdan_s37100_64.png',
  'qinggang': '_comfy_candidates/_finished_preview/icons_divine_weapons_1/qinggang_s37102_64.png', 'fangtian': '_comfy_candidates/_finished_preview/icons_divine_weapons_0/fangtian_s37001_64.png',
  'yuxi': '_comfy_candidates/_finished_preview/icons_divine_fix/yuxi_s47003_64.png', 'dilu': '_comfy_candidates/_finished_preview/icons_famous_horses_r2/dilu_s35001_64.png',
  'chitu': '_comfy_candidates/_finished_preview/icons_famous_horses/chitu_s33001_64.png', 'sunzi': '_comfy_candidates/_finished_preview/icons_books_misc/book_camp_s40002_64.png',
  'xianglong': '_comfy_candidates/_finished_preview/icons_books_misc/book_dragon_s40002_64.png', 'hengsao': '_comfy_candidates/icons_p410/sweep_all/icon_64.png',
  'jinzhong': '_comfy_candidates/icons_p410/golden_bell/icon_64.png', 'liannu': '_comfy_candidates/_finished_preview/icons_divine_weapons_0/liannu_s37002_64.png',
}

def icons():
  d = OUT / 'icons'; d.mkdir(parents=True, exist_ok=True)
  for k, p in ICONS.items():
    Image.open(HA / p).convert('RGBA').save(d / f'{k}.webp', lossless=True, method=6)
  t = Image.open(HA / 'temple_levels/exterior_lv4.png').convert('RGBA'); t = t.crop(t.getbbox())
  t.thumbnail((144, 144), Image.LANCZOS); t.save(d / 'temple.webp', quality=88, method=6)

SHOTS = [('01_horde', 'shot_horde'), ('03_boss_zhangjiao', 'shot_zhangjiao'), ('04_endless', 'shot_endless'),
         ('05_temple', 'shot_temple'), ('02_build_a', 'shot_cards'), ('02_build_b', 'shot_shop')]

def images():
  d = OUT / 'img'; d.mkdir(parents=True, exist_ok=True)
  for src, dst in SHOTS:
    im = Image.open(ROOT / 'docs/appstore/screenshots/raw/iphone69' / f'{src}.png').convert('RGB')
    for wd, suf in ((1600, ''), (720, '_s')):
      r = im.resize((wd, round(im.height * wd / im.width)), Image.LANCZOS)
      r.save(d / f'{dst}{suf}.webp', quality=80, method=6)
  ka = Image.open(HA / 'title/key_art.png').convert('RGB')
  ka.save(d / 'key_art.webp', quality=82, method=6)
  ka.resize((960, 540), Image.LANCZOS).save(d / 'key_art_s.webp', quality=80, method=6)
  # og:image 1200×630
  og = ka.resize((1200, 675), Image.LANCZOS).crop((0, 22, 1200, 652))
  og.save(d / 'og.jpg', quality=85)

def video():
  d = OUT / 'video'; d.mkdir(parents=True, exist_ok=True)
  src = HA / 'cinematics/intro_huangjin.mp4'
  subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-c:v', 'libx264', '-crf', '27', '-preset', 'slow',
                  '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '96k', str(d / 'intro.mp4')], check=True)
  subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '6', '-i', str(src), '-frames:v', '1', '-q:v', '4', str(d / 'intro_poster.jpg')], check=True)
  for a, b in (('zh-TW', 'zh-Hant'), ('zh-Hans', 'zh-Hans'), ('en', 'en'), ('ja', 'ja')):
    (d / f'intro.{b}.vtt').write_bytes((HA / f'cinematics/intro_huangjin.{a}.vtt').read_bytes())

def fonts():
  """標題字型子集：網站所有文字（index/manual/support/privacy/i18n.js）用到的字。"""
  from fontTools import subset
  d = OUT / 'fonts'; d.mkdir(parents=True, exist_ok=True)
  text = ''
  for p in list(W.glob('*.html')) + [W / 'assets/i18n.js', W / 'assets/site.js']:
    if p.exists(): text += p.read_text('utf-8')
  chars = ''.join(sorted(set(text) | set('漢末萬人敵汉末万人敌')))
  jobs = [
    (ROOT / 'steam/third_party/lxgw-wenkai-tc/LXGWWenKaiTC-Medium.ttf', 'wenkai-tc-medium.woff2', chars),
    (ROOT / 'i18n/fonts/KleeOne-SemiBold.subset.ttf', 'klee-one-semibold.woff2', chars),
    (ROOT / 'i18n/fonts/Cinzel-Bold.subset.ttf', 'cinzel-bold.woff2', chars),
  ]
  for src, name, t in jobs:
    opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']
    f = subset.load_font(str(src), opt); s = subset.Subsetter(opt); s.populate(text=t); s.subset(f)
    subset.save_font(f, str(d / name), opt)
    print(name, (d / name).stat().st_size)
  for lic in ('OFL-Cinzel.txt', 'OFL-KleeOne.txt', 'OFL-LXGWWenKai.txt'):
    (d / lic).write_bytes((ROOT / 'i18n/fonts' / lic).read_bytes())

if __name__ == '__main__':
  steps = sys.argv[1:] or ['sprites', 'icons', 'images', 'video', 'fonts']
  for s in steps: globals()[s]()
