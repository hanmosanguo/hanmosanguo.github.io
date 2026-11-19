#!/usr/bin/env python3
"""官網頁面建置（只用 Python 標準庫；zh-Hans 自動轉換需要 zhconv，可省略）。

  python3 website/tools/build_pages.py

讀：website/src/*.html（模板）、website/content/strings.json、units.json、pages/*.html、manual/*.md、
    website/assets/sprites/sprites.json
寫：website/index.html、manual.html、support.html、privacy.html、website/assets/i18n.js
模板語法：
  <tag data-i18n="key"></tag>      → 填入四種語言的 <span data-lang>（CSS 只顯示目前語言）
  <!--#head:page--> <!--#header:page--> <!--#footer-->
  <!--#mobs--> <!--#bosses--> <!--#skills:guan_yu--> <!--#manual--> <!--#page:support-->
  {{sprite:id:scale}} {{icons:a,b}} {{icon:discord}} {{shot:id:class}}
"""
import html, json, re, sys
from pathlib import Path

W = Path(__file__).resolve().parents[1]
C = W / 'content'
LANGS = ['zh-Hant', 'zh-Hans', 'en', 'ja']

try:
  import zhconv
except ImportError:
  zhconv = None

def to_hans(s):
  return zhconv.convert(s, 'zh-cn') if zhconv else s

def fill_hans(obj):
  """遞迴：有 zh-Hant 但 zh-Hans 缺或空的，自動轉。回傳是否有改。"""
  changed = False
  if isinstance(obj, dict):
    if 'zh-Hant' in obj and isinstance(obj['zh-Hant'], str) and not obj.get('zh-Hans'):
      if zhconv:
        obj['zh-Hans'] = to_hans(obj['zh-Hant']); changed = True
    for v in obj.values():
      changed |= fill_hans(v)
  elif isinstance(obj, list):
    for v in obj: changed |= fill_hans(v)
  return changed

def load_json(name):
  p = C / name
  d = json.loads(p.read_text('utf-8'))
  if fill_hans(d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', 'utf-8')
    print('已自動補 zh-Hans：', name)
  return d

S = load_json('strings.json')
U = load_json('units.json')
SPR = json.loads((W / 'assets/sprites/sprites.json').read_text('utf-8'))

def esc(s): return html.escape(s, quote=False)

def L(v, lang):
  return v.get(lang) or v.get('zh-Hant') or ''

def spans(v):
  """多語字串 → span 群；四語相同就直接輸出文字。"""
  vals = [L(v, l) for l in LANGS]
  if len(set(vals)) == 1: return esc(vals[0])
  return ''.join(f'<span data-lang="{l}" lang="{l}">{esc(x)}</span>' for l, x in zip(LANGS, vals))

def T(key):
  if key not in S: sys.exit(f'缺字串 key：{key}')
  return spans(S[key])

def sprite(sid, scale=1, extra=''):
  m = SPR[sid]
  return (f'<div class="spr{extra}" aria-hidden="true" style="--w:{m["w"]};--h:{m["h"]};--n:{m["n"]};--s:{scale};'
          f'background-image:url(assets/sprites/{sid}.webp)"></div>')


# 官方社群帳號（2026-11-19）。新增平台只要加一行。
SOCIALS = [
  ('YouTube', 'https://www.youtube.com/@hanmosanguo'),
  ('X', 'https://x.com/hanmosanguo'),
  ('Facebook', 'https://www.facebook.com/hanmosanguo'),
  ('Instagram', 'https://www.instagram.com/hanmosanguo/'),
  ('Threads', 'https://www.threads.com/@hanmosanguo'),
  ('TikTok', 'https://www.tiktok.com/@hanmosanguo'),
  ('Reddit', 'https://www.reddit.com/user/hanmosanguo/'),
  ('巴哈姆特', 'https://home.gamer.com.tw/profile/index.php?owner=hanmosanguo'),
]
def socials(foot=False):
  if foot: return ''.join(f'<li><a href="{u}" rel="noopener me" target="_blank">{n}</a></li>' for n, u in SOCIALS)
  return ''.join(f'<li><a class="soc" href="{u}" rel="noopener me" target="_blank">{n}</a></li>' for n, u in SOCIALS)

DISCORD_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M20.3 4.4A19.6 19.6 0 0 0 15.4 3l-.6 1.3a18.2 18.2 0 0 0-5.6 0L8.6 3a19.5 19.5 0 0 0-4.9 1.5C.6 9.1-.3 13.6.1 18.1a19.8 19.8 0 0 0 6 3l1.3-2a12.7 12.7 0 0 1-2-1l.5-.4a14.1 14.1 0 0 0 12.2 0l.5.4c-.6.4-1.3.7-2 1l1.3 2a19.7 19.7 0 0 0 6-3c.5-5.2-.9-9.7-3.6-13.7ZM8.3 15.3c-1.2 0-2.2-1.1-2.2-2.4s1-2.4 2.2-2.4 2.2 1.1 2.2 2.4-1 2.4-2.2 2.4Zm7.4 0c-1.2 0-2.2-1.1-2.2-2.4s1-2.4 2.2-2.4 2.2 1.1 2.2 2.4-1 2.4-2.2 2.4Z"/></svg>')

def tags_html(m):
  out = []
  for t in m.get('tags', []):
    k = {'armor': 'units.superarmor', 'fire': 'units.fire', 'ranged': 'units.ranged'}[t]
    out.append(f'<span class="tag {t}">{T(k)}</span>')
  return out

def mobs():
  cards = []
  for m in U['mobs']:
    st = ''.join(sprite(s) for s in m['sprites'])
    cards.append(f'''<article class="ucard"><div class="ustage">{st}</div><div class="ubody">
<h4 class="uname">{spans(m["name"])}</h4><div class="tags">{"".join(tags_html(m))}</div>
<p class="urow"><b>{T("units.trait")}</b>{spans(m["trait"])}</p>
<p class="urow"><b>{T("units.counter")}</b>{spans(m["counter"])}</p></div></article>''')
  return '<div class="units">\n' + '\n'.join(cards) + '\n</div>'

def bosses():
  cards = []
  for b in U['bosses']:
    cls = 'ucard' + (' final' if b.get('final') else '') + (' secret' if b.get('hidden') else '')
    tg = []
    if b.get('hidden'):
      tg.append(f'<span class="tag hidden">{T("units.hidden")}</span>')
    else:
      wave = {l: L(S['units.wave'], l).replace('{n}', str(b['wave'])) for l in LANGS}
      tg.append(f'<span class="tag wave">{spans(wave)}</span>')
      if b.get('final'): tg.append(f'<span class="tag armor">{T("units.final")}</span>')
    cards.append(f'''<article class="{cls}"><div class="ustage">{sprite(b["id"], b.get("scale", 1))}</div><div class="ubody">
<h4 class="uname">{spans(b["name"])}</h4><div class="tags">{"".join(tg)}</div>
<p class="urow moves"><b>{T("units.skills")}</b>{spans(b["moves"])}</p>
<p class="urow"><b>{T("units.trait")}</b>{spans(b["trait"])}</p>
<p class="urow"><b>{T("units.counter")}</b>{spans(b["counter"])}</p></div></article>''')
  return '<div class="units bosses">\n' + '\n'.join(cards) + '\n</div>'

def skills(hero):
  li = []
  for s in U['heroes'][hero]:
    inn = f'<em>{T("heroes.innate")}</em>' if s.get('innate') else ''
    li.append(f'<li><img src="assets/icons/{s["icon"]}.webp" width="48" height="48" alt="" loading="lazy">'
              f'<div><b>{spans(s["name"])}{inn}</b><span class="sd">{spans(s["d"])}</span></div></li>')
  return '<ul class="skills">' + ''.join(li) + '</ul>'

def icons(names):
  out = []
  for n in names.split(','):
    if n == 'temple':
      out.append('<img src="assets/icons/temple.webp" alt="" loading="lazy" style="grid-column:span 2;width:72px;height:auto;border:0;background:none">')
    else:
      out.append(f'<img src="assets/icons/{n}.webp" width="34" height="34" alt="" loading="lazy">')
  return ''.join(out)

def shot(sid, cls):
  return (f'<figure class="shot {cls}"><a href="assets/img/shot_{sid}.webp" data-lb="shot.{sid}">'
          f'<img src="assets/img/shot_{sid}_s.webp" srcset="assets/img/shot_{sid}_s.webp 720w, assets/img/shot_{sid}.webp 1600w" '
          f'sizes="(min-width: 760px) 50vw, 100vw" width="1600" height="736" alt="" loading="lazy"></a>'
          f'<figcaption>{T("shot." + sid)}</figcaption></figure>')

# ---------- Markdown（說明書） ----------
def inline(s):
  s = esc(s)
  s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
  s = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<em>\1</em>', s)
  s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
  return s

def md_to_html(md, lang):
  lines = md.splitlines()
  out, toc, para, quote = [], [], [], []
  stack = []  # [(indent, tag)]
  n2 = n3 = 0
  def flush_para():
    if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
  def flush_quote():
    if quote: out.append('<blockquote>' + ''.join(f'<p>{inline(q)}</p>' for q in quote) + '</blockquote>'); quote.clear()
  def close_lists(to=-1):
    while stack and stack[-1][0] > to:
      out.append(f'</li></{stack.pop()[1]}>')
  for raw in lines:
    line = raw.rstrip()
    if not line.strip():
      flush_para(); flush_quote(); continue
    m = re.match(r'^(#{1,4})\s+(.*)$', line)
    if m:
      flush_para(); flush_quote(); close_lists()
      lv, txt = len(m.group(1)), m.group(2)
      hid = ''
      if lv == 2: n2 += 1; n3 = 0; hid = f's{n2}'
      elif lv == 3: n3 += 1; hid = f's{n2}-{n3}'
      elif lv == 4: hid = f's{n2}-{n3}-x{len(out)}'
      if lv in (2, 3): toc.append((lv, hid, txt))
      tag = 'h1' if lv == 1 else f'h{lv}'
      out.append(f'<{tag} id="{lang}-{hid}">{inline(txt)}</{tag}>' if hid else f'<{tag}>{inline(txt)}</{tag}>')
      continue
    if re.match(r'^\s*---+\s*$', line):
      flush_para(); flush_quote(); close_lists(); out.append('<hr>'); continue
    if line.startswith('>'):
      flush_para(); close_lists(); quote.append(line.lstrip('>').strip()); continue
    m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', line)
    if m:
      flush_para(); flush_quote()
      ind, mark, txt = len(m.group(1)), m.group(2), m.group(3)
      tag = 'ol' if mark[0].isdigit() else 'ul'
      if stack and ind < stack[-1][0]: close_lists(ind)
      if not stack or ind > stack[-1][0]:
        out.append(f'<{tag}><li>'); stack.append((ind, tag))
      else:
        if stack[-1][1] != tag:
          out.append(f'</li></{stack.pop()[1]}><{tag}><li>'); stack.append((ind, tag))
        else:
          out.append('</li><li>')
      out.append(inline(txt)); continue
    if stack and raw.startswith(' '):  # 清單項目的續行
      out.append('<br>' + inline(line.strip())); continue
    close_lists(); flush_quote(); para.append(line.strip())
  flush_para(); flush_quote(); close_lists()
  return '\n'.join(out), toc

def manual():
  arts = []
  for lang in LANGS:
    md = (C / 'manual' / f'manual.{lang}.md').read_text('utf-8')
    md = re.sub(r'^<!--.*?-->\s*', '', md, flags=re.S)
    body, toc = md_to_html(md, lang)
    items = ''.join(f'<li class="l{lv}"><a href="#{lang}-{hid}">{inline(re.sub(r"\*\*", "", t))}</a></li>' for lv, hid, t in toc)
    arts.append(f'''<div class="doc with-toc" data-lang="{lang}" lang="{lang}">
<aside class="toc"><nav><details open><summary>{esc(L(S["manual.toc"], lang))}</summary><ol>{items}</ol></details></nav></aside>
<article class="prose">{body}</article></div>''')
  return '\n'.join(arts)

def page(name):
  out = []
  for lang in LANGS:
    p = C / 'pages' / f'{name}.{lang}.html'
    if not p.exists() and lang == 'zh-Hans':
      src = (C / 'pages' / f'{name}.zh-Hant.html').read_text('utf-8')
      if zhconv:
        p.write_text(to_hans(src), 'utf-8'); print('已自動產生', p.name)
      else:
        p = C / 'pages' / f'{name}.zh-Hant.html'
    out.append(f'<div class="doc" data-lang="{lang}" lang="{lang}"><article class="prose">{p.read_text("utf-8")}</article></div>')
  return '\n'.join(out)

PAGES = {
  'index': ('meta.title', 'meta.desc'),
  'manual': ('manual.title', 'meta.desc'),
  'support': ('support.title', 'meta.desc'),
  'privacy': ('privacy.title', 'meta.desc'),
}

def head(pg):
  tk, dk = PAGES[pg]
  t = L(S[tk], 'zh-Hant')
  if pg != 'index': t += '｜' + L(S['game.name'], 'zh-Hant') + '：' + L(S['game.chapter'], 'zh-Hant')
  h = (W / 'src/_head.html').read_text('utf-8')
  return (h.replace('{{title}}', html.escape(t)).replace('{{desc}}', html.escape(L(S[dk], 'zh-Hant')))
           .replace('{{page}}', '' if pg == 'index' else pg + '.html')
           + f'<meta name="hm-page" content="{pg}">')

def render(pg):
  s = (W / 'src' / f'{pg}.html').read_text('utf-8')
  s = s.replace(f'<!--#head:{pg}-->', head(pg))
  s = s.replace(f'<!--#header:{pg}-->', (W / 'src/_header.html').read_text('utf-8').replace('{{home}}', '' if pg == 'index' else 'index.html'))
  s = s.replace('<!--#footer-->', (W / 'src/_footer.html').read_text('utf-8'))
  s = s.replace('<!--#mobs-->', mobs() if '<!--#mobs-->' in s else '')
  s = s.replace('<!--#bosses-->', bosses() if '<!--#bosses-->' in s else '')
  s = re.sub(r'<!--#skills:(\w+)-->', lambda m: skills(m.group(1)), s)
  if '<!--#manual-->' in s: s = s.replace('<!--#manual-->', manual())
  s = re.sub(r'<!--#page:(\w+)-->', lambda m: page(m.group(1)), s)
  s = re.sub(r'\{\{sprite:(\w+):(\d+)\}\}', lambda m: sprite(m.group(1), int(m.group(2))), s)
  s = re.sub(r'\{\{icons:([\w,]+)\}\}', lambda m: icons(m.group(1)), s)
  s = s.replace('{{icon:discord}}', DISCORD_SVG)
  s = s.replace('{{socials:foot}}', socials(True)).replace('{{socials}}', socials())
  s = re.sub(r'\{\{shot:(\w+):(\w*)\}\}', lambda m: shot(m.group(1), m.group(2)), s)
  s = re.sub(r'<(\w+)([^<>]*?)\sdata-i18n="([^"]+)"([^<>]*)></\1>',
             lambda m: f'<{m.group(1)}{m.group(2)} data-i18n="{m.group(3)}"{m.group(4)}>{T(m.group(3))}</{m.group(1)}>', s)
  left = re.findall(r'\{\{[^}]+\}\}|<!--#[^>]+-->', s)
  if left: sys.exit(f'{pg}: 未處理的模板標記 {left}')
  (W / f'{pg}.html').write_text(s, 'utf-8')
  print('寫入', pg + '.html', len(s.encode()) // 1024, 'KB')

def i18n_js():
  d = {l: {k: L(v, l) for k, v in S.items() if not k.startswith('_')} for l in LANGS}
  (W / 'assets/i18n.js').write_text('/* 由 tools/build_pages.py 產生，請改 content/strings.json */\nwindow.HM_I18N=' +
                                    json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ';\n', 'utf-8')

if __name__ == '__main__':
  i18n_js()
  for pg in PAGES: render(pg)
