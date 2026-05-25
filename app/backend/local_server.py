from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from app.backend.functions.api import lambda_handler


CORS_HEADERS = {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type,x-floci-user",
}


def build_lambda_event(*, method: str, path: str, headers: dict[str, str], body: bytes) -> dict[str, Any]:
    return {
        "requestContext": {"http": {"method": method.upper(), "path": path}},
        "headers": {key.lower(): value for key, value in headers.items()},
        "body": body.decode("utf-8") if body else None,
        "isBase64Encoded": False,
    }


class LocalApiHandler(BaseHTTPRequestHandler):
    server_version = "FlociCloudLabLocalApi/0.1"

    def do_OPTIONS(self) -> None:
        self._send_json(204, "")

    def do_GET(self) -> None:
        self._proxy_to_lambda()

    def do_POST(self) -> None:
        self._proxy_to_lambda()

    def _proxy_to_lambda(self) -> None:
        body_length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(body_length) if body_length else b""
        event = build_lambda_event(
            method=self.command,
            path=self.path.split("?", 1)[0],
            headers={key: value for key, value in self.headers.items()},
            body=body,
        )
        response = lambda_handler(event, None)
        self._send_json(response["statusCode"], response.get("body", ""), response.get("headers", {}))

    def _send_json(self, status_code: int, body: str, headers: dict[str, str] | None = None) -> None:
        self.send_response(status_code)
        for key, value in {**CORS_HEADERS, **(headers or {})}.items():
            self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        print(f"local-api {self.address_string()} - {format % args}")


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), LocalApiHandler)
    print(json.dumps({"service": "floci-cloud-lab-local-api", "url": f"http://{host}:{port}"}))
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Floci Cloud Lab local API adapter")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
