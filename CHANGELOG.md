# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-17

First release.

### Added
- `build` command: turn one RPG Maker 2000/2003 game folder into a self-contained
  web build (EasyRPG WASM player + staged game + `index.json` + a play page).
- Reliable asset loading: a service worker (`/games/` cache-first) plus an on-load
  precache step download every game file into the cache up front, so images never
  silently go missing on a plain static host.
- Audio that works out of the box: a free General MIDI soundfont (GeneralUser GS)
  is downloaded on first build for MIDI music; `--soundfont` for a custom `.sf2`,
  `--no-soundfont` to skip. An audio-unlock shim resumes audio on the first click.
- `serve` command: threaded local preview server.
- `serve --share`: expose the build on a real HTTPS URL via a Cloudflare quick
  tunnel (needs `cloudflared`) — reproduces the deployed experience, audio included.
- `iframe` embed snippet printed after a build.
