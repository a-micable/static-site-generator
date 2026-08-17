"""Development server exposing the JSON API for the React dashboard."""

from __future__ import annotations

import argparse
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ssg.api import SiteApi

logger = logging.getLogger(__name__)


class ApiHandler(BaseHTTPRequestHandler):
    api: SiteApi

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), format % args)

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes | None:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return None
        return self.rfile.read(length)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        status, payload = self.api.dispatch("GET", self.path)
        self._send_json(status, payload)

    def do_PUT(self) -> None:
        status, payload = self.api.dispatch("PUT", self.path, self._read_body())
        self._send_json(status, payload)

    def do_POST(self) -> None:
        status, payload = self.api.dispatch("POST", self.path, self._read_body())
        self._send_json(status, payload)


def create_handler(api: SiteApi) -> type[ApiHandler]:
    return type("BoundApiHandler", (ApiHandler,), {"api": api})


def main() -> int:
    parser = argparse.ArgumentParser(description="SSG React dashboard API server")
    parser.add_argument(
        "source",
        nargs="?",
        default=os.environ.get("SSG_SOURCE", "example-site"),
        help="Site source directory",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    source = Path(args.source).resolve()
    api = SiteApi(source)
    handler = create_handler(api)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    logger.info("API server listening on http://%s:%s (source=%s)", args.host, args.port, source)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down API server")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
