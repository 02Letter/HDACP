from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from uuid import uuid4

spec = importlib.util.spec_from_file_location('visits_server', Path(__file__).resolve().parents[1] / 'server/visits.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class VisitsServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'visitors.sqlite3'
        self.secret = b'test-secret-only-not-for-deployment'
        self.counter = backend.Counter(self.path, self.secret)

    def tearDown(self):
        self.directory.cleanup()

    def test_same_ip_and_browser_count_once_and_survive_restart(self):
        browser = str(uuid4())
        self.assertEqual(self.counter.record('192.0.2.1', browser), 1)
        self.assertEqual(self.counter.record('192.0.2.1', browser), 1)
        self.assertEqual(backend.Counter(self.path, self.secret).count(), 1)
        self.assertEqual(self.counter.record('192.0.2.1', str(uuid4())), 2)
        self.assertEqual(self.counter.record('192.0.2.2', browser), 3)

    def test_concurrent_requests_do_not_duplicate_visitors(self):
        browser = str(uuid4())
        with ThreadPoolExecutor(max_workers=8) as pool:
            counts = list(pool.map(lambda _: self.counter.record('192.0.2.1', browser), range(20)))
        self.assertEqual(set(counts), {1})

    def test_raw_identifiers_are_not_persisted(self):
        browser = str(uuid4())
        self.counter.record('192.0.2.111', browser)
        with self.counter.connect() as db:
            saved = str(db.execute('SELECT * FROM visitors').fetchall())
        self.assertNotIn(browser, saved)
        self.assertNotIn('192.0.2.111', saved)

    def test_api_origin_validation_and_repeat_visits(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), backend.handler_for(self.counter))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        browser = str(uuid4())
        def request(method, origin, body=None):
            connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
            headers = {'Origin': origin, 'Content-Type': 'application/json', 'X-Real-IP': '192.0.2.1'}
            connection.request(method, backend.API_PATH, json.dumps(body) if body else None, headers)
            response = connection.getresponse()
            result = response.status, response.getheader('Access-Control-Allow-Origin'), json.loads(response.read())
            connection.close()
            return result
        try:
            self.assertEqual(request('OPTIONS', backend.ORIGIN)[:2], (200, backend.ORIGIN))
            self.assertEqual(request('POST', 'https://unrelated.example', {'browserId': browser})[0], 403)
            for _ in range(2):
                self.assertEqual(request('POST', backend.ORIGIN, {'browserId': browser})[2], {'count': 1})
            self.assertEqual(request('POST', backend.ORIGIN, {'browserId': 'invalid'})[0], 400)
            self.assertEqual(request('GET', backend.ORIGIN)[2], {'count': 1})
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
