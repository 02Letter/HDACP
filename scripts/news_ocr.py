"""Read public college news posters. OCR evidence stays in an ignored cache.

Only original title/date/link and matched roster names are published by the caller.
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from threading import Lock
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

VERSION = 'rapidocr-1.4.4-news-v1'
MAX_BYTES = 12_000_000
MAX_PIXELS = 30_000_000


class NewsImageLimit(ValueError):
    """A known processing limit: keep this article as a candidate, not a source outage."""


def image_url_allowed(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.hostname == 'cs.qhu.edu.cn'
            and parsed.port in (None, 443) and not parsed.username and not parsed.password
            and parsed.path.startswith('/images/')
            and Path(parsed.path).suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'))


def qualified_lines(lines, threshold):
    return [line for line in lines if isinstance(line.get('text'), str)
            and float(line.get('score', 0)) >= threshold]


class CollegeImageRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not image_url_allowed(newurl):
            raise ValueError('News image redirect leaves the college image directory')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class NewsOCR:
    def __init__(self, cache_dir, relevant=None):
        # Fail at startup if explicitly enabled but dependencies are unavailable.
        from PIL import Image
        import numpy as np
        from rapidocr_onnxruntime import RapidOCR
        self.Image, self.np = Image, np
        self.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=1,
                               det_limit_side_len=640, max_side_len=1600)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.relevant = relevant
        self.stats = {'processed': 0, 'cached': 0}

    def read(self, url):
        if not image_url_allowed(url):
            raise ValueError('News image is outside the permitted college image directory')
        cache_path = self.cache_dir / (sha256((VERSION + url).encode()).hexdigest() + '.json')
        cached = {}
        if cache_path.exists():
            try:
                cached = json.loads(cache_path.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                pass
        headers = {'User-Agent': 'HDACP-public-news-OCR/1.0 (+https://github.com/02Letter/HDACP)'}
        # A partial positive scan remains usable only while the current roster still
        # confirms it. Roster changes can require a full scan on the next run.
        if cached and not cached.get('complete', True) and (
                self.relevant is None or not self.relevant(cached.get('lines', []))):
            cached = {}
        if cached.get('etag'):
            headers['If-None-Match'] = cached['etag']
        if cached.get('modified'):
            headers['If-Modified-Since'] = cached['modified']
        try:
            with build_opener(CollegeImageRedirect()).open(Request(url, headers=headers), timeout=25) as response:
                if not image_url_allowed(response.url):
                    raise ValueError('Unexpected news image redirect')
                if not (response.headers.get_content_type() or '').startswith('image/'):
                    raise ValueError('News image response is not an image')
                raw = response.read(MAX_BYTES + 1)
                etag, modified = response.headers.get('ETag'), response.headers.get('Last-Modified')
        except HTTPError as exc:
            if exc.code == 304 and 'lines' in cached:
                with self.lock:
                    self.stats['cached'] += 1
                return cached['lines']
            raise RuntimeError(f'News image HTTP {exc.code}') from None
        if len(raw) > MAX_BYTES:
            raise NewsImageLimit('News image exceeds download limit')
        digest = sha256(raw).hexdigest()
        if cached.get('digest') == digest and 'lines' in cached:
            with self.lock:
                self.stats['cached'] += 1
            return cached['lines']
        image = self.Image.open(BytesIO(raw))
        if image.width * image.height > MAX_PIXELS or image.width < 20 or image.height < 20:
            raise NewsImageLimit('News image dimensions outside limits')
        image = image.convert('RGB')
        if image.width > 1200:
            image = image.resize((1200, round(image.height * 1200 / image.width)))
        lines = []
        complete = True
        # Long posters need overlapping tiles so small Chinese characters remain legible.
        with self.lock:
            for top in range(0, image.height, 1350):
                tile = image.crop((0, max(0, top - 60), image.width, min(top + 1410, image.height)))
                result, _ = self.engine(self.np.asarray(tile))
                lines.extend({'text': row[1], 'score': round(float(row[2]), 4)} for row in (result or []))
                if self.relevant is not None and self.relevant(lines):
                    complete = top + 1410 >= image.height
                    break
            self.stats['processed'] += 1
        cache = {'version': VERSION, 'url': url, 'digest': digest, 'etag': etag,
                 'modified': modified, 'lines': lines, 'complete': complete}
        with self.lock:
            tmp = cache_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
            tmp.replace(cache_path)
        return lines
