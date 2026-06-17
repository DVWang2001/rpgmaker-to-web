"""Command-line interface for rpgmaker-to-web."""
from __future__ import annotations

import argparse

from . import webify


def _build(args) -> int:
    soundfont = None if args.no_soundfont else (args.soundfont or webify.AUTO_SOUNDFONT)
    out = webify.build(args.game_dir, out=args.output, title=args.title,
                       soundfont=soundfont, refresh_player=args.refresh_player)
    print("\nNext steps:")
    print(f"  Preview locally:  rpgmaker-to-web serve {out}")
    print(f"  Embed in a page:  {webify.iframe_snippet()}")
    print(f"  Or upload the '{out}' folder to any static host (see README).")
    return 0


CLOUDFLARED_HELP = (
    "--share needs 'cloudflared' (Cloudflare's free quick-tunnel tool), which wasn't found.\n"
    "Install it, then run the same command again:\n"
    "  Windows:  winget install --id Cloudflare.cloudflared\n"
    "  macOS:    brew install cloudflared\n"
    "  Linux:    https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/\n"
)


def _make_httpd(args):
    import functools
    import http.server

    # Threaded: the player fires many concurrent asset requests; a single-threaded
    # server blocks under that load and the page hangs on reload.
    # Deliberately NO COOP/COEP here: the build's primary use is an embeddable
    # iframe, and cross-origin isolation can't be enabled from inside an iframe on
    # an arbitrary parent — so the game must (and does) run without it.
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=args.directory)
    return http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)


def _serve(args) -> int:
    httpd = _make_httpd(args)
    local_url = f"http://localhost:{args.port}"
    print(f"Serving '{args.directory}' at {local_url}/  (Ctrl+C to stop)")

    # Plain local preview: good for a quick visual check. Note that browsers apply
    # a stricter autoplay policy to localhost, so audio may be partial here even
    # though it's fine once hosted. Use --share for a faithful, audio-complete test.
    if not getattr(args, "share", False):
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
        finally:
            httpd.server_close()
        return 0

    # --share: expose the same files on a real HTTPS URL via a Cloudflare quick
    # tunnel — no upload, no account. A real origin behaves like proper hosting
    # (HTTP/2, normal autoplay rules), so it reproduces the deployed experience.
    import shutil
    import subprocess
    import threading

    cloudflared = shutil.which("cloudflared")
    if not cloudflared:
        print("\n" + CLOUDFLARED_HELP + "\nServing locally only for now (Ctrl+C to stop).")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
        finally:
            httpd.server_close()
        return 0

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print("\nOpening a Cloudflare quick tunnel — watch for the")
    print("  https://<something>.trycloudflare.com")
    print("URL in the box below. Open it, click the game once, and you get the full")
    print("hosted experience (images + music + SFX). Ctrl+C to stop.\n")
    proc = None
    try:
        proc = subprocess.Popen([cloudflared, "tunnel", "--url", local_url])
        proc.wait()
    except KeyboardInterrupt:
        print("\nstopping…")
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        httpd.shutdown()
        httpd.server_close()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="rpgmaker-to-web",
        description="Turn an RPG Maker 2000/2003 game into a webpage you can play and share.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {webify.__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a game folder into web files")
    b.add_argument("game_dir", help="the RPG Maker game folder (contains RPG_RT.ldb/.lmt)")
    b.add_argument("-o", "--output", default="dist", help="output folder (default: dist)")
    b.add_argument("--title", default=None, help="page title (default: game folder name)")
    b.add_argument("--soundfont", default=None,
                   help="path to a custom .sf2 soundfont (default: a free soundfont, downloaded once)")
    b.add_argument("--no-soundfont", action="store_true",
                   help="build without a soundfont (MIDI music will be silent)")
    b.add_argument("--refresh-player", action="store_true", help="re-download the EasyRPG player")
    b.set_defaults(func=_build)

    s = sub.add_parser("serve", help="preview a built folder locally")
    s.add_argument("directory", nargs="?", default="dist", help="folder to serve (default: dist)")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--share", action="store_true",
                   help="also expose a real HTTPS URL via a Cloudflare quick tunnel "
                        "(needs cloudflared; reproduces the hosted experience incl. audio)")
    s.set_defaults(func=_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
