"""
Main HTTP Server & REST API for Ofrenda AI
Serves the luminous frontend and local REST endpoints for Altar state & Gemma 2 inference.
Runs completely offline with standard Python 3 library.
"""

import os
import sys
import json
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any

from gemma_engine import GemmaEngine
from altar_store import AltarStore

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

engine = GemmaEngine()
store = AltarStore()

class OfrendaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def send_error_json(self, message: str, status: int = 400):
        self.send_json({"error": message}, status=status)

    def read_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # API Routes
        if path == "/api/status":
            return self.send_json(engine.get_status())

        elif path == "/api/altars":
            return self.send_json(store.load_all())

        elif path.startswith("/api/altars/") and not path.endswith("/export"):
            altar_id = path.replace("/api/altars/", "").strip()
            altar = store.get_altar(altar_id)
            if altar:
                return self.send_json(altar)
            return self.send_error_json("Altar not found", 404)

        elif path.startswith("/api/altars/") and path.endswith("/export"):
            parts = path.split("/")
            altar_id = parts[3]
            altar = store.get_altar(altar_id)
            if not altar:
                return self.send_error_json("Altar not found", 404)
            
            # Generate standalone archival HTML
            archive_html = self.generate_archival_html(altar)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="ofrenda_{altar_id}_archive.html"')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(archive_html.encode("utf-8"))
            return

        # Serve frontend files
        if path == "" or path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self.read_body()

        if path == "/api/altars":
            created = store.create_altar(body)
            return self.send_json(created, status=201)

        elif path == "/api/altars/reset":
            reset = store.reset_defaults()
            return self.send_json(reset)

        elif "/candles/" in path and path.endswith("/toggle"):
            # /api/altars/<id>/candles/<candle_id>/toggle
            parts = path.split("/")
            altar_id = parts[3]
            candle_id = parts[5]
            candle = store.toggle_candle(altar_id, candle_id)
            if candle:
                return self.send_json(candle)
            return self.send_error_json("Candle or altar not found", 404)

        elif path.startswith("/api/altars/") and path.endswith("/offerings"):
            # /api/altars/<id>/offerings
            parts = path.split("/")
            altar_id = parts[3]
            offering = store.add_offering(altar_id, body)
            if offering:
                return self.send_json(offering, status=201)
            return self.send_error_json("Altar not found", 404)

        elif path.startswith("/api/altars/") and path.endswith("/commune"):
            # /api/altars/<id>/commune
            parts = path.split("/")
            altar_id = parts[3]
            altar = store.get_altar(altar_id)
            if not altar:
                return self.send_error_json("Altar not found", 404)

            user_msg = body.get("message", "We remember you tonight. How does it feel across the veil?")
            resp = engine.generate_remembrance(
                spirit_name=altar.get("name", "Departed Soul"),
                spirit_title=altar.get("title", "Honored Spirit"),
                spirit_traits=altar.get("traits", ""),
                spirit_memories=altar.get("memories", ""),
                user_message=user_msg,
                persona_key=altar.get("persona_key")
            )
            return self.send_json(resp)

        return self.send_error_json("Endpoint not found", 404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self.read_body()

        if path.startswith("/api/altars/"):
            altar_id = path.replace("/api/altars/", "").strip()
            updated = store.update_altar(altar_id, body)
            if updated:
                return self.send_json(updated)
            return self.send_error_json("Altar not found", 404)

        return self.send_error_json("Endpoint not found", 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if "/offerings/" in path:
            # /api/altars/<id>/offerings/<offering_id>
            parts = path.split("/")
            altar_id = parts[3]
            offering_id = parts[5]
            if store.remove_offering(altar_id, offering_id):
                return self.send_json({"success": True})
            return self.send_error_json("Offering not found", 404)

        return self.send_error_json("Endpoint not found", 404)

    def generate_archival_html(self, altar: Dict[str, Any]) -> str:
        """Create a 100% self-contained offline memorial archive."""
        name = altar.get("name", "Departed Soul")
        title = altar.get("title", "")
        years = altar.get("years", "")
        offerings = altar.get("offerings", [])
        candles = altar.get("candles", [])
        
        offerings_html = "".join([
            f"""<div class="offering-card">
                <div class="off-type">{o.get('type', 'offering').upper()} &bull; {o.get('tier', 'tier').upper()} TIER</div>
                <div class="off-name">{o.get('name', '')}</div>
                <div class="off-note">{o.get('note', '')}</div>
            </div>"""
            for o in offerings
        ])

        candles_html = "".join([
            f"""<div class="candle-pill {'lit' if c.get('lit') else 'unlit'}">
                🕯️ {c.get('label', 'Candle')} ({'LIT' if c.get('lit') else 'EXTINGUISHED'})
            </div>"""
            for c in candles
        ])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Archival Altar &mdash; {name}</title>
<style>
  body {{
    background: #0d0914;
    color: #f7e6ca;
    font-family: 'Georgia', serif;
    margin: 0;
    padding: 40px 20px;
    display: flex;
    justify-content: center;
  }}
  .container {{
    max-width: 760px;
    width: 100%;
    background: rgba(26, 17, 37, 0.95);
    border: 2px solid #e08b26;
    box-shadow: 0 0 35px rgba(224, 139, 38, 0.35);
    border-radius: 12px;
    padding: 35px;
  }}
  h1 {{ color: #ffa62b; margin: 0 0 5px 0; text-align: center; font-size: 2.2rem; }}
  .subtitle {{ text-align: center; color: #d4a373; font-style: italic; margin-bottom: 25px; }}
  .years {{ text-align: center; color: #ffbe0b; font-weight: bold; letter-spacing: 2px; margin-bottom: 30px; }}
  .archival-badge {{
    background: #2a1b3d;
    border: 1px dashed #ffa62b;
    padding: 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    color: #e0d0c0;
    margin-bottom: 30px;
    text-align: center;
  }}
  .section-title {{
    color: #ffaa00;
    border-bottom: 1px solid rgba(255, 170, 0, 0.3);
    padding-bottom: 6px;
    margin-top: 30px;
    font-size: 1.2rem;
  }}
  .offering-card {{
    background: rgba(45, 27, 66, 0.7);
    border-left: 4px solid #e08b26;
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 4px;
  }}
  .off-type {{ font-size: 0.7rem; color: #e76f51; letter-spacing: 1px; }}
  .off-name {{ font-size: 1.1rem; color: #fff; font-weight: bold; margin: 4px 0; }}
  .off-note {{ font-size: 0.95rem; color: #ddd; }}
  .candles-wrap {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
  .candle-pill {{
    background: #1b1226;
    border: 1px solid #ffbe0b;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
  }}
  .candle-pill.lit {{ box-shadow: 0 0 10px rgba(255, 190, 11, 0.5); color: #ffbe0b; }}
  .memory-box {{
    background: rgba(15, 10, 22, 0.8);
    border: 1px solid #7209b7;
    padding: 18px;
    border-radius: 6px;
    line-height: 1.6;
    font-size: 1.05rem;
  }}
  footer {{
    margin-top: 40px;
    text-align: center;
    font-size: 0.8rem;
    color: #8d7b9d;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="archival-badge">
    🕯️ <strong>Offline Archival Record &mdash; Ofrenda AI</strong><br>
    This sacred memory document requires no server, no internet, and no proprietary cloud. It lives forever on your personal storage.
  </div>
  <h1>{name}</h1>
  <div class="subtitle">{title}</div>
  <div class="years">{years}</div>

  <div class="section-title">Sacred Candles</div>
  <div class="candles-wrap">
    {candles_html}
  </div>

  <div class="section-title">Enduring Memories & Traits</div>
  <div class="memory-box">
    <p><strong>Memories:</strong> {altar.get('memories', '')}</p>
    <p><strong>Spiritual Traits:</strong> {altar.get('traits', '')}</p>
  </div>

  <div class="section-title">Offerings Placed on the Altar (Tiers)</div>
  {offerings_html}

  <footer>
    Ofrenda AI &bull; Preserved with local open-weight intelligence &bull; Día de los Muertos 2026
  </footer>
</div>
</body>
</html>"""


def run_server(port: int = 8080):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, OfrendaHandler)
    print(f"\n=======================================================")
    print(f"🕯️  OFRENDA AI — GHOST IN THE MACHINE (LOCAL SERVER) 🕯️")
    print(f"=======================================================")
    print(f"✦ Active URL:     http://localhost:{port}")
    print(f"✦ Gemma Engine:   {engine.active_model or 'Local Fallback'}")
    print(f"✦ Privacy Mode:   100% Offline & Private (Local Inference)")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nExtinguishing candles. Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
