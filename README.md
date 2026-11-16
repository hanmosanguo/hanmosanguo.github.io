# 《漢末萬人敵》官方網站（靜態，GitHub Pages）

整個 `website/` 資料夾（除了 `_shots/`）複製到 GitHub 倉庫根目錄即可上線，網址 `https://hanmosanguo.github.io/`。全部用相對路徑，沒有任何第三方腳本、追蹤或 Cookie；字型自帶（SIL OFL 授權檔在 `assets/fonts/`）。

| 頁面 | 用途 |
|---|---|
| `index.html` | 首頁：主視覺、特色、英雄、兵種與渠帥、營寨寶物、截圖與開場影片、社群、平台與售價 |
| `manual.html` | 完整遊戲說明書（四種語言，附目錄） |
| `support.html` | 支援與常見問題（**App Store「支援網址」用這頁**） |
| `privacy.html` | 隱私權政策（**App Store「隱私權政策網址」用這頁**） |

語言：繁中／简中／English／日本語。預設依瀏覽器語言，選過會記在瀏覽器（localStorage），也可用網址參數 `?lang=zh-Hant|zh-Hans|en|ja` 指定。

## 最常改的三件事（直接改 `assets/site.js` 開頭，不用重建）

1. **工作室名稱**（定案：蒼曜遊戲工作室／AzureHalo Studio）：`assets/site.js` 的 `STUDIO` 一行全站生效（頁尾版權）；HTML 裡 `data-studio` 的預設字也同步改過。Logo：`assets/img/studio_logo.png`（原檔 `docs/brand/azurehalo_logo_1254.png`），放在各頁頁尾。
2. **商店連結**：`STORES` 裡的 `steam`／`ios`／`mac`／`gplay`，`null`＝顯示「即將推出」，填網址後該平台按鈕自動變成「前往商店」。
3. **Discord 邀請、聯絡信箱**：`SITE.discord`、`SITE.email`（頁面上的連結會自動套用；`content/pages/*.html` 與 `src/*.html` 裡寫死的文字若要換，也一併搜尋取代）。

## 改文字內容（要重建，只需 Python 3 標準庫）

- 首頁文案：`content/strings.json`（每個 key 有四種語言）。
- 兵種、渠帥、英雄武技：`content/units.json`。
- 支援頁、隱私權：`content/pages/<頁>.<語言>.html`。
- 說明書：`content/manual/manual.<語言>.md`（繁中來源＝repo 根目錄 `遊戲說明書_三國演義篇.md`，其他語言＝`i18n/help/help.*.md`；遊戲說明書改了就重新複製過來，英日簡記得刪掉第一行 `<!--i18n-map ...-->`）。
- 版面骨架：`src/*.html`（`_head`／`_header`／`_footer` 是共用片段）。

改完執行：

```
python3 website/tools/build_pages.py
```

會重新產生 `index.html`、`manual.html`、`support.html`、`privacy.html` 與 `assets/i18n.js`。
**zh-Hans 自動轉**：字串表的 `zh-Hans` 留空、或刪掉 `content/pages/*.zh-Hans.html`，有安裝 `zhconv`（`pip install zhconv`）時會自動從繁中轉出並寫回；之後可以直接手改。

## 重建圖片／動畫／影片／字型（需要 Pillow、fonttools、brotli、ffmpeg）

> `build_assets.py` 要在遊戲 repo 裡（`website/` 位於 repo 根目錄下）才能跑，因為它讀 `huangjin_assets/` 等遊戲素材；`build_pages.py` 則可以在獨立的網站倉庫單獨跑。`.nojekyll` 讓 GitHub Pages 不經 Jekyll 處理，請保留。

```
python3 website/tools/build_assets.py            # 全部
python3 website/tools/build_assets.py sprites    # 只重切兵種動畫條
python3 website/tools/build_assets.py fonts      # 改過文字後若出現缺字（豆腐），重跑這個
```

- 兵種／渠帥動畫：從遊戲實際讀的精靈圖（`huangjin_assets/enemies/sheets/*_walk_4dir_6f.png`、`bosses/*/animations/idle/`）切出朝南（騎兵朝東）一列，存成 `assets/sprites/<id>.webp` 橫條，CSS `steps()` 循環播放、`image-rendering: pixelated`。新增兵種：在 `build_assets.py` 的 `SPRITES` 加一行，再到 `units.json` 加一張卡。
- 截圖：`docs/appstore/screenshots/raw/iphone69/`（無標語版）→ `assets/img/shot_*.webp`。
- 主視覺：`huangjin_assets/title/key_art.png`；`og.jpg` 是 Discord／社群分享預覽圖。
- 開場影片：`huangjin_assets/cinematics/intro_huangjin.mp4` 重新壓縮＋四語字幕 vtt。
- 標題字型：霞鶩文楷 TC（`steam/third_party/lxgw-wenkai-tc/`）、Klee One、Cinzel，依網站實際用到的字子集化成 woff2。

## 本機預覽與截圖驗證

```
cd website && python3 -m http.server 8917 --bind 127.0.0.1
```

瀏覽 http://127.0.0.1:8917/ 。截圖放 `_shots/`（不進 git）。
