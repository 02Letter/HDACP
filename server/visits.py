"""Small persistent visitor counter, served behind the existing HTTPS proxy.

Only Python's standard library is needed. The database stores HMAC digests,
never the original IP address or the browser identifier.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import os
from pathlib import Path
import secrets
import sqlite3
from uuid import UUID

API_PATH = '/hdacp-visits/api/visits'
ORIGIN = 'https://02letter.github.io'


class Counter:
    def __init__(self, path, secret):
        self.path, self.secret = str(path), secret
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE IF NOT EXISTS visitors (digest TEXT PRIMARY KEY, first_seen TEXT NOT NULL)')

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def count(self):
        with self.connect() as db:
            return db.execute('SELECT COUNT(*) FROM visitors').fetchone()[0]

    def record(self, ip, browser_id):
        identifier = UUID(browser_id)
        if identifier.version != 4:
            raise ValueError('A version 4 browser UUID is required')
        address = ipaddress.ip_address(ip)
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            address = address.ipv4_mapped
        digest = hmac.new(self.secret, f'{address}|{identifier}'.encode(), hashlib.sha256).hexdigest()
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO visitors VALUES (?, ?)',
                       (digest, datetime.now(timezone.utc).isoformat()))
            return db.execute('SELECT COUNT(*) FROM visitors').fetchone()[0]


def handler_for(counter, origin=ORIGIN):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # Avoid recording IP addresses, request bodies or browser identifiers.
            print(f'visits {self.command} {self.path.split("?")[0]}', flush=True)

        def respond(self, status, body=None):
            payload = json.dumps(body or {}, separators=(',', ':')).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Vary', 'Origin')
            self.send_header('X-Content-Type-Options', 'nosniff')
            if self.headers.get('Origin') == origin:
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def permitted(self, require_origin=False):
            if self.path != API_PATH:
                self.respond(404, {'error': 'not_found'})
                return False
            supplied = self.headers.get('Origin')
            if supplied not in (None, origin) or (require_origin and supplied != origin):
                self.respond(403, {'error': 'origin_not_allowed'})
                return False
            return True

        def do_OPTIONS(self):
            if self.permitted(require_origin=True):
                self.respond(200)

        def do_GET(self):
            if self.permitted():
                try:
                    self.respond(200, {'count': counter.count()})
                except sqlite3.Error:
                    self.respond(503, {'error': 'temporarily_unavailable'})

        def do_POST(self):
            if not self.permitted(require_origin=True):
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 512 or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    self.respond(400, {'error': 'invalid_request'})
                    return
                body = json.loads(self.rfile.read(length))
                browser_id = body.get('browserId') if isinstance(body, dict) else None
                if not isinstance(browser_id, str) or len(browser_id) != 36:
                    raise ValueError('Invalid browser identifier')
                peer_ip = self.client_address[0]
                # Nginx must overwrite X-Real-IP with $remote_addr. Never trust it
                # on requests arriving directly from a non-loopback address.
                ip = self.headers.get('X-Real-IP', peer_ip) if ipaddress.ip_address(peer_ip).is_loopback else peer_ip
                count = counter.record(ip, browser_id)
            except (ValueError, TypeError, UnicodeError):
                self.respond(400, {'error': 'invalid_request'})
                return
            except sqlite3.Error:
                self.respond(503, {'error': 'temporarily_unavailable'})
                return
            self.respond(200, {'count': count})

    return Handler


def load_secret(path):
    if not path.exists():
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(descriptor, 'wb') as file:
                file.write(secrets.token_bytes(32))
    secret = path.read_bytes()
    if len(secret) != 32:
        raise ValueError('Invalid persistent counter secret')
    return secret


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    directory = Path(args.data_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    counter = Counter(directory / 'visitors.sqlite3', load_secret(directory / 'counter.secret'))
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(counter))
    print(f'Visitor counter listening on loopback port {args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
