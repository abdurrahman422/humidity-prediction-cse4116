from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import webbrowser
import sys
import joblib
from humidity_model import ROOT, OUT, predict

saved = joblib.load(OUT / "humidity_model.joblib")


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type="application/json"):
        if isinstance(body, dict):
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.reply(200, (ROOT / "humidity_ui.html").read_bytes(), "text/html")
        elif self.path == "/api/info":
            summary = json.loads((OUT / "summary.json").read_text())
            self.reply(200, {"districts": saved["districts"], "metrics": summary})
        else:
            self.reply(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/predict":
            return self.reply(404, {"error": "Not found"})
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 4096:
                raise ValueError("Invalid input size")
            values = json.loads(self.rfile.read(size))
            if not isinstance(values, dict):
                raise ValueError("Expected form inputs")
            self.reply(200, predict(values, saved))
        except (ValueError, TypeError) as error:
            self.reply(400, {"error": str(error)})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Open http://127.0.0.1:8765", flush=True)
    if "--open" in sys.argv:
        webbrowser.open("http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
