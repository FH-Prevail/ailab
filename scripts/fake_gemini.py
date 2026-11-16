"""A stand-in for the Gemini API, for testing notebook 3 without a key.

    python3 scripts/fake_gemini.py 0     # prints the port it listens on

It lists two model names and, for every question, first asks for one tool call
(carrier_scorecard for Italy), then answers with a fixed text that names the tools it
was offered. Real answers come only from the real Gemini; this checks the plumbing.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class FakeGemini(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply({"models": [{"name": "models/gemini-3.5-flash-lite", "supportedActions": ["generateContent"]},
                               {"name": "models/gemini-3.8-flash", "supportedActions": ["generateContent"]}]})

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        answered = any("functionResponse" in part for content in request.get("contents", [])
                       for part in content.get("parts", []))
        tools = [d["name"] for t in request.get("tools", []) for d in t.get("functionDeclarations", [])]
        if answered:
            part = {"text": "Stand-in answer (not a real model). Tools offered: " + ", ".join(tools)}
        else:
            part = {"functionCall": {"name": "carrier_scorecard", "args": {"country": "IT"}}}
        self.reply({"candidates": [{"content": {"role": "model", "parts": [part]}, "finishReason": "STOP"}],
                    "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 1, "totalTokenCount": 2}})


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 0), FakeGemini)
    print(server.server_address[1], flush=True)
    server.serve_forever()
