/* =====================================================================
 * 漢末萬人敵 官網設定 —— 改這裡就全站生效
 * ===================================================================== */

// 工作室名稱（2026-11-16 定案：蒼曜遊戲工作室／AzureHalo Studio；zh＝繁中與日文、hans＝簡中、en＝英文）
const STUDIO = { zh: '蒼曜遊戲工作室', hans: '苍曜游戏工作室', en: 'AzureHalo Studio' };

// 商店連結：null＝顯示「即將推出」；填入網址後該平台按鈕自動變成可點的「前往商店」
const STORES = {
  steam: null,   // 例：'https://store.steampowered.com/app/XXXXXXX/'
  ios: null,     // 例：'https://apps.apple.com/app/idXXXXXXXXX'
  mac: null,     // Mac App Store（若和 iOS 同一個 App 記錄，可填同一個網址）
  gplay: null,   // 例：'https://play.google.com/store/apps/details?id=XXXX'
};

const SITE = {
  discord: 'https://discord.gg/j6zhhXjq9u',
  email: 'hanmosanguo@gmail.com',
  year: 2026,
};

/* ===================================================================== */
(function () {
  'use strict';
  const LANGS = ['zh-Hant', 'zh-Hans', 'en', 'ja'];
  const doc = document.documentElement;
  const I = window.HM_I18N || null;

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function t(key, lang) { const d = I && (I[lang] || I['zh-Hant']); return (d && d[key]) || ''; }

  function applyLang(lang) {
    if (LANGS.indexOf(lang) < 0) lang = 'zh-Hant';
    doc.lang = lang;
    // 標題與描述
    const pg = (document.querySelector('meta[name="hm-page"]') || {}).content || 'index';
    const titleKey = { index: 'meta.title', manual: 'manual.title', support: 'support.title', privacy: 'privacy.title' }[pg];
    if (I && titleKey) {
      let title = t(titleKey, lang);
      if (pg !== 'index') title += (lang === 'en' ? ' | ' : '｜') + t('game.name', lang) + (lang === 'en' ? ': ' : lang === 'ja' ? ' ―' : '：') + t('game.chapter', lang) + (lang === 'ja' ? '―' : '');
      document.title = title;
      const md = document.querySelector('meta[name="description"]'); if (md) md.content = t('meta.desc', lang);
    }
    // 屬性翻譯：data-i18n-attr="aria-label:key;title:key2"
    if (I) document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      el.getAttribute('data-i18n-attr').split(';').forEach(pair => { const [a, k] = pair.split(':'); if (a && k) el.setAttribute(a.trim(), t(k.trim(), lang)); });
    });
    // 語言按鈕
    document.querySelectorAll('[data-setlang]').forEach(b => b.setAttribute('aria-pressed', String(b.getAttribute('data-setlang') === lang)));
    // 工作室名稱
    const sn = lang === 'en' ? STUDIO.en : lang === 'zh-Hans' ? (STUDIO.hans || STUDIO.zh) : STUDIO.zh;
    document.querySelectorAll('[data-studio]').forEach(el => { el.textContent = sn; });
    // 影片預設字幕跟語言走
    const v = document.getElementById('intro');
    if (v && v.textTracks) for (const tr of v.textTracks) tr.mode = tr.language === lang ? 'showing' : 'hidden';
  }

  function setLang(lang) {
    store('hm_lang', lang); applyLang(lang);
    try { const u = new URL(location.href); if (u.searchParams.has('lang')) { u.searchParams.set('lang', lang); history.replaceState(null, '', u); } } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyLang(doc.lang);
    document.querySelectorAll('[data-setlang]').forEach(b => b.addEventListener('click', () => setLang(b.getAttribute('data-setlang'))));

    // 連結、信箱、年份
    document.querySelectorAll('a[data-discord]').forEach(a => { a.href = SITE.discord; });
    document.querySelectorAll('a[data-email]').forEach(a => { a.href = 'mailto:' + SITE.email; if (!a.children.length && a.textContent.indexOf('@') >= 0) a.textContent = SITE.email; else a.querySelectorAll('span').forEach(sp => { if (sp.textContent.indexOf('@') >= 0) sp.textContent = SITE.email; }); });
    document.querySelectorAll('[data-year]').forEach(el => { el.textContent = SITE.year; });

    // 商店按鈕
    document.querySelectorAll('[data-store]').forEach(el => {
      const url = STORES[el.getAttribute('data-store')];
      if (!url) return;
      const a = document.createElement('a');
      a.className = el.className; a.href = url; a.rel = 'noopener'; a.target = '_blank';
      a.innerHTML = el.innerHTML; el.replaceWith(a);
      const s = a.querySelector('.ps'); if (s) { s.setAttribute('data-i18n', 'plat.get'); s.innerHTML = LANGS.map(l => '<span data-lang="' + l + '" lang="' + l + '">' + t('plat.get', l) + '</span>').join(''); }
    });

    // 說明書目錄：窄螢幕預設收合
    if (innerWidth < 1000) document.querySelectorAll('.toc details[open]').forEach(d => d.removeAttribute('open'));

    // 手機選單
    const top = document.querySelector('.top'), mb = document.querySelector('.menu-btn');
    if (top && mb) {
      mb.addEventListener('click', () => { const o = top.classList.toggle('open'); mb.setAttribute('aria-expanded', String(o)); });
      top.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', () => { top.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); }));
    }

    // 截圖放大
    const lb = document.getElementById('lightbox');
    if (lb) {
      const img = lb.querySelector('img'), cap = lb.querySelector('p');
      const close = () => { lb.classList.remove('open'); img.removeAttribute('src'); };
      document.querySelectorAll('a[data-lb]').forEach(a => a.addEventListener('click', e => {
        e.preventDefault(); img.src = a.getAttribute('href'); cap.textContent = t(a.getAttribute('data-lb'), doc.lang); lb.classList.add('open');
        lb.querySelector('[data-close]').focus();
      }));
      lb.addEventListener('click', e => { if (e.target === lb || e.target.hasAttribute('data-close')) close(); });
      document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    }
  });
})();
