"""Look up publication titles and DOI metadata without trusting old venue labels.

All matches remain reviewable in the report. This does not change lab attribution.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from datetime import date
from publication_metadata import normalize, metadata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'src/data'
CACHE = ROOT / '.backups/publication-metadata-cache'


def manual_key(paper):
    return 'manual:' + sha256(paper['content'].encode()).hexdigest()[:20]


def title_of(paper):
    return re.sub(r'[（(](?:CCF|SCI|EI|CSCD|中文核心|中科院)[^）)]*[）)]\s*$', '',
                  re.sub(r'^\[[^\]]*\]\s*', '', paper.get('title') or paper.get('content', ''))).strip()


def get(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'HDACP-metadata-review/1.0 (https://github.com/02Letter/HDACP)',
                                              'Accept': 'application/json'}), timeout=35) as response:
                value = json.load(response)['message']
            path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            return value
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def compact(work):
    return {key: work.get(key) for key in ('DOI', 'title', 'container-title', 'short-container-title', 'event',
                                          'author', 'published', 'published-print', 'published-online', 'URL', 'link', 'type')}


def lookup(item):
    key, paper = item
    title = title_of(paper)
    doi = paper.get('doi', '').removeprefix('https://doi.org/')
    try:
        if doi:
            works = [get('https://api.crossref.org/works/' + quote(doi, safe=''))]
        else:
            query = urlencode({'query.title': title, 'rows': 5})
            works = get('https://api.crossref.org/works?' + query)['items']
        matches = sorted([(SequenceMatcher(None, normalize(title), normalize((w.get('title') or [''])[0])).ratio(), w)
                          for w in works], key=lambda pair: pair[0], reverse=True)
        best = matches[0] if matches else (0, {})
        return {'key': key, 'requestedTitle': title, 'score': best[0], 'exact': best[0] == 1,
                'record': compact(best[1]), 'candidates': [compact(w) for _, w in matches[:3]]}
    except Exception as exc:
        return {'key': key, 'requestedTitle': title, 'error': type(exc).__name__}


def verified_auto(paper, result):
    """Never turn a similar title or an unrelated same-title article into a source."""
    record = result.get('record') or {}
    doi = paper.get('doi', '').removeprefix('https://doi.org/').lower()
    source_authors = {normalize(a) for a in paper.get('authors', [])}
    publisher_authors = {normalize(a.get('given', '') + ' ' + a.get('family', '')) for a in record.get('author') or []}
    return bool(doi and doi == record.get('DOI', '').lower()
                and result.get('exact') and source_authors & publisher_authors
                and record.get('container-title'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default=str(ROOT / '.backups/publication-audit.json'))
    parser.add_argument('--update', action='store_true', help='Verify only new automatic papers and save their publisher metadata')
    args = parser.parse_args()
    manual = json.loads((DATA / 'publications.json').read_text(encoding='utf-8'))
    auto = json.loads((DATA / 'auto-publications.json').read_text(encoding='utf-8'))
    metadata_path = DATA / 'publication-metadata.json'
    saved = json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else {}
    items = [(p['id'], p) for p in auto if p['id'] not in saved] if args.update else (
        [(p.get('id') or manual_key(p), p) for g in manual for p in g['items']] + [(p['id'], p) for p in auto])
    papers = dict(items)
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i, result in enumerate(pool.map(lookup, items), 1):
            results.append(result)
            if args.update:
                result['approved'] = verified_auto(papers[result['key']], result)
                if result['approved']:
                    saved[result['key']] = metadata(result['record'], date.today().isoformat())
            if i % 10 == 0 or i == len(items):
                print(f'Metadata reviewed {i}/{len(items)}; exact matches {sum(r.get("exact", False) for r in results)}', flush=True)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.update:
        metadata_path.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Approved:', sum(r.get('approved', False) for r in results), '; held for review:', sum(not r.get('approved') for r in results))
    print('Report:', args.report, flush=True)


if __name__ == '__main__':
    main()
