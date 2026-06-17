# rpgmaker-to-web

**English** | [繁體中文](#繁體中文)

Turn an **RPG Maker 2000/2003** game into a webpage you can **play in the browser**
and **embed anywhere** — with one command. No plugins, no installers, no app store.

```bash
rpgmaker-to-web build "path/to/MyGame"
rpgmaker-to-web serve dist --share      # get a real https:// link to play & share
```

Under the hood it packages your game with the [EasyRPG](https://easyrpg.org/) WASM
player and wires up everything needed to make it load reliably and sound right.

---

## Why a web version?

You already have the game running on Windows. Why put it on the web?

- **Anyone can play, on anything.** A link opens on Windows, Mac, ChromeOS, Android,
  iPhone/iPad — no download, no "unknown publisher" warnings, no install.
- **iPhone/iPad without a Mac.** You can't make a native iOS app without a Mac and
  a paid developer account. A web page sidesteps all of that.
- **Embed it in your own site.** Drop the game into a blog post or itch-style page
  with a single `<iframe>`.
- **Nothing to maintain on the player's side.** No EasyRPG install, no RTP setup —
  it's all bundled into the page.

The trade-off: web audio has a touch more latency than the desktop player, and the
default soundfont differs slightly from Windows' built-in one (see [Audio](#audio)).

## Requirements

- **Python 3.9+**
- Internet on the first build (it downloads the EasyRPG player and a soundfont, then
  caches them).
- For `serve --share`: [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
  (free). Install with `winget install --id Cloudflare.cloudflared` /
  `brew install cloudflared`.

## Install

```bash
pip install rpgmaker-to-web
```

Or run from a clone without installing:

```bash
git clone https://github.com/DVWang2001/rpgmaker-to-web
cd rpgmaker-to-web
python -m rpgmaker_to_web --help
```

## Usage

### Build

```bash
rpgmaker-to-web build "path/to/MyGame" -o dist
```

`MyGame` is the folder containing `RPG_RT.ldb` / `RPG_RT.lmt`. The result is a
self-contained `dist/` folder you can host anywhere.

| Option | Meaning |
| --- | --- |
| `-o, --output DIR` | Output folder (default: `dist`) |
| `--title TEXT` | Page title (default: the game folder name) |
| `--soundfont FILE.sf2` | Use a custom soundfont instead of the default |
| `--no-soundfont` | Build without a soundfont (MIDI music will be silent) |
| `--refresh-player` | Re-download the EasyRPG player |

### Preview locally

```bash
rpgmaker-to-web serve dist            # http://localhost:8000
rpgmaker-to-web serve dist --port 9000
```

Good for a quick visual check. **Note:** browsers apply a stricter audio policy to
`localhost`, so sound may be partial here even though it's fine once hosted. For a
faithful test, use `--share`.

### Preview on a real HTTPS link (recommended for testing audio)

```bash
rpgmaker-to-web serve dist --share
```

This starts the local server **and** opens a free [Cloudflare quick
tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/use-cases/quick-tunnels/),
printing a `https://<random>.trycloudflare.com` URL. Open it, click the game once,
and you get the full deployed experience — images, music, and sound effects —
without uploading anything. Stop with `Ctrl+C` and the link disappears.

### Embed in a page

After a build, an `<iframe>` snippet is printed. It looks like:

```html
<iframe src="index.html" width="640" height="480"
        style="border:0;aspect-ratio:4/3;max-width:100%" allowfullscreen></iframe>
```

Point `src` at wherever you host the `dist/` folder.

## Host it (beginner-friendly)

The `dist/` folder is just static files — any static host works. Three easy, free
options:

**GitHub Pages**
1. Create a repo and upload the contents of `dist/` (so `index.html` is at the repo
   root, or in a `/docs` folder).
2. Repo → **Settings → Pages** → set the source branch (and `/docs` if you used it).
3. Your game is at `https://<you>.github.io/<repo>/`.

**Netlify Drop** — no account setup needed
1. Go to <https://app.netlify.com/drop>.
2. Drag your `dist/` folder onto the page.
3. You get an instant `https://<name>.netlify.app` link.

**Cloudflare Pages**
1. <https://pages.cloudflare.com> → create a project → **Direct Upload**.
2. Upload the `dist/` folder.
3. You get a `https://<name>.pages.dev` link.

All three serve over HTTPS, which is what the player wants for full audio.

## Audio

Most RPG Maker 2000/2003 games use **MIDI** music, which needs a *soundfont* to make
sound. On the first build, rpgmaker-to-web downloads a free, redistributable one —
[GeneralUser GS](https://github.com/mrbumpy409/GeneralUser-GS) — (cached, then copied
into the build output). Pass `--soundfont your.sf2` to use a different one.

Browsers don't start audio until you interact with the page; the build handles this
by resuming audio on your **first click or key press**, so just click the game once.
If you hear nothing on `localhost`, that's the browser's `localhost` audio policy —
test with `--share` or after hosting, where it works normally.

## How it works

```
build  →  download/cache EasyRPG player (WASM)
       →  stage the game folder (skipping junk/hidden files)
       →  download/cache a soundfont, place it as easyrpg.soundfont
       →  generate index.json (the player's asset manifest)
       →  write a service worker + precache-<slug>.json
       →  write index.html: player + audio-unlock + SW registration + precache
```

The **precache + service worker** is the important part: the player streams many
asset requests at once, and some fail silently against a plain static server (you'd
get missing images with no error). Precaching every file into the cache first, then
serving `/games/` cache-first, makes loading reliable everywhere.

## Development

```bash
pip install pytest
pytest            # tests run offline (no downloads)
```

The code is small and dependency-free, under the `rpgmaker_to_web/` package:
`cli.py`, `webify.py`, `staging.py`, `player_fetch.py`, `soundfont_fetch.py`,
`gencache.py`.

## Credits & license

- Game playback by the [**EasyRPG Player**](https://easyrpg.org/) (GPLv3).
- Default soundfont: [**GeneralUser GS**](https://github.com/mrbumpy409/GeneralUser-GS)
  by S. Christian Collins (free to redistribute; downloaded at build time).

This project is licensed under the **GNU General Public License v3.0 or later** —
see [LICENSE](LICENSE).

---

# 繁體中文

[English](#rpgmaker-to-web) | **繁體中文**

一行指令,把 **RPG Maker 2000/2003** 遊戲變成可在**瀏覽器直接遊玩**、又能**嵌入任何網頁**
的網頁版。免外掛、免安裝、不必上架。

```bash
rpgmaker-to-web build "path/to/MyGame"
rpgmaker-to-web serve dist --share      # 取得真的 https:// 連結來玩與分享
```

底層用 [EasyRPG](https://easyrpg.org/) 的 WASM 播放器打包你的遊戲,並把「能穩定載入、
聲音正常」所需的一切都接好。

---

## 為什麼要網頁版?

遊戲在 Windows 上明明能跑,為什麼還要做網頁版?

- **誰都能玩、什麼裝置都能玩。** 一個連結就能在 Windows、Mac、ChromeOS、Android、
  iPhone/iPad 上開啟 —— 不用下載、沒有「來源不明」警告、免安裝。
- **iPhone/iPad 不需要 Mac。** 沒有 Mac 和付費開發者帳號就無法做原生 iOS App,
  網頁版完全繞過這個限制。
- **嵌進你自己的網站。** 用一個 `<iframe>` 就能把遊戲放進部落格文章或作品頁。
- **玩家端零維護。** 不必裝 EasyRPG、不必設定 RTP —— 全部打包進網頁裡。

代價:網頁音訊的延遲比桌面版略高,且預設 soundfont 的音色和 Windows 內建的略有不同
(見 [音訊](#音訊))。

## 需求

- **Python 3.9+**
- 首次 build 需要網路(會下載 EasyRPG 播放器和 soundfont,之後快取)。
- 使用 `serve --share` 需要
  [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)(免費)。
  安裝:`winget install --id Cloudflare.cloudflared` / `brew install cloudflared`。

## 安裝

```bash
pip install rpgmaker-to-web
```

或從原始碼直接跑(不安裝):

```bash
git clone https://github.com/DVWang2001/rpgmaker-to-web
cd rpgmaker-to-web
python -m rpgmaker_to_web --help
```

## 用法

### 打包(build)

```bash
rpgmaker-to-web build "path/to/MyGame" -o dist
```

`MyGame` 是含有 `RPG_RT.ldb` / `RPG_RT.lmt` 的遊戲資料夾。產出一個獨立的 `dist/`
資料夾,放到任何主機都能跑。

| 選項 | 說明 |
| --- | --- |
| `-o, --output DIR` | 輸出資料夾(預設 `dist`) |
| `--title TEXT` | 網頁標題(預設為遊戲資料夾名) |
| `--soundfont FILE.sf2` | 改用自訂 soundfont |
| `--no-soundfont` | 不含 soundfont(MIDI 音樂會沒聲音) |
| `--refresh-player` | 重新下載 EasyRPG 播放器 |

### 本機預覽

```bash
rpgmaker-to-web serve dist            # http://localhost:8000
rpgmaker-to-web serve dist --port 9000
```

適合快速看畫面。**注意:** 瀏覽器對 `localhost` 的音訊政策較嚴,這裡聲音可能不完整,
但上線後就正常。要忠實測試請用 `--share`。

### 用真 HTTPS 連結預覽(測音訊推薦)

```bash
rpgmaker-to-web serve dist --share
```

這會啟動本機伺服器**並**開一條免費的
[Cloudflare 快速通道](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/use-cases/quick-tunnels/),
印出一個 `https://<隨機>.trycloudflare.com` 網址。打開它、點一下遊戲畫面,就能得到
跟正式上線一樣的完整體驗 —— 圖片、音樂、音效 —— 完全不用上傳。按 `Ctrl+C` 連結即消失。

### 嵌入網頁

build 完會印出 `<iframe>` 程式碼,長這樣:

```html
<iframe src="index.html" width="640" height="480"
        style="border:0;aspect-ratio:4/3;max-width:100%" allowfullscreen></iframe>
```

把 `src` 指向你放 `dist/` 的位置即可。

## 部署(新手友善)

`dist/` 就是一堆靜態檔案 —— 任何靜態主機都能用。三個簡單免費的選擇:

**GitHub Pages**
1. 建一個 repo,把 `dist/` 裡的內容上傳(讓 `index.html` 在 repo 根目錄,或 `/docs`)。
2. Repo →**Settings → Pages**→設定來源分支(若用 `/docs` 也選它)。
3. 你的遊戲就在 `https://<你>.github.io/<repo>/`。

**Netlify Drop** —— 不用註冊設定
1. 開 <https://app.netlify.com/drop>。
2. 把 `dist/` 資料夾拖進去。
3. 立刻得到 `https://<名稱>.netlify.app` 連結。

**Cloudflare Pages**
1. <https://pages.cloudflare.com> →建立專案→**Direct Upload**。
2. 上傳 `dist/` 資料夾。
3. 得到 `https://<名稱>.pages.dev` 連結。

三者都走 HTTPS,正是播放器要完整音訊所需的環境。

## 音訊

多數 RPG Maker 2000/2003 遊戲用 **MIDI** 音樂,需要 *soundfont* 才會出聲。首次 build
時,rpgmaker-to-web 會下載一個可自由重分發的免費 soundfont ——
[GeneralUser GS](https://github.com/mrbumpy409/GeneralUser-GS)(快取後複製進輸出的 build)。
用 `--soundfont your.sf2` 可換成別的。

瀏覽器在你與頁面互動前不會啟動音訊;本工具會在你**第一次點擊或按鍵**時喚醒音訊,
所以點一下遊戲即可。若在 `localhost` 完全沒聲音,那是瀏覽器對 `localhost` 的音訊政策
所致 —— 用 `--share` 或部署上線後即正常。

## 運作原理

```
build  →  下載/快取 EasyRPG 播放器(WASM)
       →  搬入遊戲資料夾(略過垃圾/隱藏檔)
       →  下載/快取 soundfont,放成 easyrpg.soundfont
       →  產生 index.json(播放器的素材清單)
       →  寫入 service worker + precache-<slug>.json
       →  寫入 index.html:播放器 + 音訊喚醒 + SW 註冊 + precache
```

**precache + service worker** 是關鍵:播放器會同時送出大量素材請求,在陽春靜態
伺服器上有些會靜默失敗(於是缺圖卻沒有任何錯誤)。先把每個檔案灌進快取、再讓
`/games/` 走 cache-first,載入就能處處穩定。

## 開發

```bash
pip install pytest
pytest            # 測試全離線(不會下載)
```

程式碼精簡、零相依,集中在 `rpgmaker_to_web/` 套件:`cli.py`、`webify.py`、
`staging.py`、`player_fetch.py`、`soundfont_fetch.py`、`gencache.py`。

## 致謝與授權

- 遊戲播放由 [**EasyRPG Player**](https://easyrpg.org/) 提供(GPLv3)。
- 預設 soundfont:[**GeneralUser GS**](https://github.com/mrbumpy409/GeneralUser-GS),
  作者 S. Christian Collins(可自由重分發;於 build 時下載)。

本專案採用 **GNU General Public License v3.0 或更新版本** 授權 ——
見 [LICENSE](LICENSE)。
