"""Sync public scholarly metadata and college news; never rewrite manual content.

Python 3.11+, standard library only. HTTPS_PROXY is supported for local use.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import unescape
from html.parser import HTMLParser
import json
from itertools import zip_longest
import os
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'src/data'
USER_AGENT = 'HDACP-public-content-sync/1.0 (+https://github.com/02Letter/HDACP)'


def read_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write_json(path, value):
    content = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(content, encoding='utf-8', newline='\n')
    tmp.replace(path)
    return True


def normalize(text):
    text = unescape(re.sub(r'<[^>]*>', '', text or ''))
    return ''.join(c for c in unicodedata.normalize('NFKD', text).lower() if c.isalnum())


def manual_title(text):
    text = re.sub(r'^\[[^\]]+\]\s*', '', text)
    return re.split(r'[（(](?:CCF|SCI|EI)', text, flags=re.I)[0]


def safe_url(url, hosts=None):
    parsed = urlparse(url or '')
    return parsed.scheme in ('http', 'https') and bool(parsed.hostname) and (
        hosts is None or parsed.hostname in hosts)


def fetch(url, as_json=False):
    for attempt in range(3):
        try:
            req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json' if as_json else 'text/html'})
            with urlopen(req, timeout=25) as response:
                raw = response.read(8_000_001)
                if len(raw) > 8_000_000:
                    raise ValueError('Response too large')
                charset = response.headers.get_content_charset() or 'utf-8'
            text = raw.decode(charset)
            if as_json:
                value = json.loads(text)  # HTTP 200 bot challenges must not be accepted.
                if not isinstance(value, dict) or not isinstance(value.get('results'), list):
                    raise ValueError('Unexpected API response')
                return value
            return text
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f'HTTP {exc.code} from {urlparse(url).hostname}') from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError(f'Network error from {urlparse(url).hostname}') from None
        time.sleep(2 ** attempt)


def fetch_works(filters, getter=fetch):
    cursor, seen = '*', set()
    works = []
    for _ in range(30):
        params = {'filter': filters, 'per_page': 100, 'cursor': cursor, 'sort': 'publication_date:desc'}
        if os.getenv('OPENALEX_API_KEY'):
            params['api_key'] = os.environ['OPENALEX_API_KEY']
        response = getter('https://api.openalex.org/works?' + urlencode(params), as_json=True)
        works.extend(response['results'])
        cursor = response.get('meta', {}).get('next_cursor')
        if not cursor or not response['results']:
            return works
        if cursor in seen:
            raise ValueError('Repeated OpenAlex cursor')
        seen.add(cursor)
    raise ValueError('OpenAlex pagination limit reached; no partial results accepted')


def affiliated(authorship, institution):
    return any((i.get('id') or '').rsplit('/', 1)[-1] == institution for i in authorship.get('institutions', []))


def teacher_matches(authorship, teachers, institution):
    if not affiliated(authorship, institution):
        return []
    author = authorship.get('author') or {}
    name = normalize(author.get('display_name'))
    author_id = (author.get('id') or '').rsplit('/', 1)[-1]
    orcids = {(o or '').rsplit('/', 1)[-1] for o in [author.get('orcid'), *author.get('observed_orcids', [])]}
    return [t['name'] for t in teachers if name in {normalize(a) for a in t['aliases']} and (
        author_id in t['authorIds'] or bool(orcids & set(t['orcids'])))]


def paper_record(work, config, roster, today):
    published = work.get('publication_date') or ''
    try:
        day = date.fromisoformat(published)
    except ValueError:
        return None, 'missing-date'
    if day > today or published < config['since']:
        return None, 'outside-date-range'
    if work.get('type') not in ('article', 'conference-paper', 'proceedings-article', 'book-chapter', 'review') or work.get('is_retracted'):
        return None, 'excluded-type-or-retraction'
    authorships = work.get('authorships', [])
    teachers = [t for t in config['teachers'] if any(p.get('id') == t['memberId'] and p['name'] == t['name'] for p in roster['teachers'])]
    matched = sorted({name for a in authorships for name in teacher_matches(a, teachers, config['institution'])})
    if not matched:
        return None, 'unverified-author-or-affiliation'
    # Student names are contextual coauthor matches, not standalone verified identities.
    student_names = {s['name'] for s in roster['students']}
    coauthors = sorted({name for a in authorships if affiliated(a, config['institution'])
                        for name, aliases in config['studentAliases'].items()
                        if name in student_names and normalize((a.get('author') or {}).get('display_name')) in {normalize(x) for x in aliases}})
    title = (work.get('display_name') or '').strip()
    link = work.get('doi') or work.get('id')
    if not title or not safe_url(link, {'doi.org', 'openalex.org'}):
        return None, 'missing-title-or-source'
    source = (work.get('primary_location') or {}).get('source') or {}
    return {
        'id': work['id'], 'title': title, 'date': published, 'year': published[:4],
        'venue': source.get('display_name') or '', 'link': link, 'doi': work.get('doi') or '',
        'authors': [(a.get('author') or {}).get('display_name', '') for a in authorships],
        'members': matched, 'studentCoauthors': coauthors, 'source': 'OpenAlex',
        'sourceUrl': work['id']
    }, None


class CollegeHTML(HTMLParser):
    """Only use the college's article body for name matching, not global navigation."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.links = []
        self.parts = []
        self.headings = []
        self.all_text = []
        self.anchor = None
        self.has_body = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('br', 'img', 'meta', 'link', 'input', 'hr', 'source', 'wbr'):
            return
        classes = attrs.get('class', '').split()
        is_body = 'article' in classes or attrs.get('id') in ('vsb_content', 'vsb_content_2')
        self.has_body |= is_body
        self.stack.append((tag, is_body))
        if tag == 'a':
            self.anchor = {'href': attrs.get('href', ''), 'text': []}

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            self.links.append((self.anchor['href'], ''.join(self.anchor['text']).strip()))
            self.anchor = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        if any(t in ('script', 'style') for t, _ in self.stack):
            return
        self.all_text.append(text)
        if any(b for _, b in self.stack):
            self.parts.append(text)
        if any(t in ('h1', 'h2') for t, _ in self.stack):
            self.headings.append(text)
        if self.anchor is not None:
            self.anchor['text'].append(text)


def parse_news(html, url, title, config, roster, today):
    page = CollegeHTML()
    page.feed(html)
    if not page.has_body:
        raise ValueError('College article body missing; markup may have changed')
    body = ''.join(page.parts)
    title = ''.join(page.headings).strip() or title
    stamp = re.search(r'(?:发布日期|发布时间|时间)\s*[：:]\s*(\d{4})[-年/](\d{1,2})[-月/](\d{1,2})', ''.join(page.all_text))
    if not stamp:
        raise ValueError('College publication date missing')
    published = date(*map(int, stamp.groups()))
    if published > today or published.isoformat() < config['since']:
        return None, 'outside-date-range'
    names = sorted({p['name'] for p in [*roster['teachers'], *roster['students']] if p['name'] in body})
    lab_match = any(k.lower() in (title + body).lower() for k in config['labKeywords'])
    teachers = {p['name'] for p in roster['teachers']}
    # A common student name by itself is not enough to establish lab attribution.
    if not (lab_match or bool(set(names) & teachers) or len(names) >= 2):
        return None, 'insufficient-member-evidence'
    return {'id': 'college-' + urlparse(url).path.rsplit('/', 1)[-1].split('.')[0],
            'date': published.isoformat(), 'title': title, 'link': url,
            'members': names, 'source': '青海大学计算机学院'}, None


def news_links(html, index):
    page = CollegeHTML()
    page.feed(html)
    links = []
    for href, title in page.links:
        url = urljoin(index, href)
        if safe_url(url, {'cs.qhu.edu.cn'}) and re.search(r'/[a-f0-9]{32}\.htm$', urlparse(url).path) and title:
            links.append((url, title))
    if not links:
        raise ValueError('No college article links; markup may have changed')
    return list(dict.fromkeys(links))


def merge_records(old, incoming, manual, kind, config, today):
    manual_keys = {normalize(manual_title(p['content']) if kind == 'papers' else p['title']) for p in manual}
    manual_links = {p.get('link', '').rstrip('/') for p in manual if p.get('link')}
    records = {p['id']: p for p in old}
    records.update({p['id']: p for p in incoming})
    kept, seen = [], set()
    for record in sorted(records.values(), key=lambda p: (p['date'], p['id']), reverse=True):
        key = normalize(record['title'])
        link = record['link'].rstrip('/')
        if key in seen or key in manual_keys or link in manual_links:
            continue
        # Also catch manually written citations which include authors and venue after the title.
        if kind == 'papers' and len(key) > 35 and any(key in m for m in manual_keys):
            continue
        if not (config['since'] <= record['date'] <= today.isoformat()):
            continue
        kept.append(record)
        seen.add(key)
    return kept


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default=str(ROOT / '.backups/sync-report.json'))
    args = parser.parse_args()
    config = read_json(ROOT / 'config/content-sources.json')
    roster = read_json(DATA / 'team.json')
    today = date.today()
    report = {'date': today.isoformat(), 'rosterNames': [p['name'] for p in [*roster['teachers'], *roster['students']]],
              'teacherSources': config['teachers'], 'errors': [], 'candidates': [], 'counts': {}}
    papers, articles = [], []
    retracted = set()
    works = {}
    ids = '|'.join(sorted({i for t in config['teachers'] for i in t['authorIds']}))
    orcids = '|'.join(sorted({i for t in config['teachers'] for i in t['orcids']}))
    filters = [f'author.id:{ids}', f'authorships.author.orcid:{orcids}']
    for query in filters:
        try:
            results = fetch_works(query + f",from_publication_date:{config['since']},to_publication_date:{today.isoformat()}")
            works.update({w['id']: w for w in results})
        except Exception as exc:
            # Never include API keys or full request URLs in diagnostic output.
            report['errors'].append({'source': 'OpenAlex', 'error': type(exc).__name__})
    for work in works.values():
        if work.get('is_retracted'):
            retracted.add(work['id'])
        record, reason = paper_record(work, config, roster, today)
        if record:
            papers.append(record)
        else:
            report['candidates'].append({'kind': 'paper', 'title': work.get('display_name'), 'sourceUrl': work.get('id'), 'reason': reason})
    links = {}
    index_links = []
    for index in config['newsIndexes']:
        try:
            index_links.append(news_links(fetch(index), index))
        except Exception as exc:
            report['errors'].append({'source': index, 'error': type(exc).__name__})
    # Give each column equal coverage instead of spending the article budget on one column.
    for row in zip_longest(*index_links):
        for item in row:
            if item:
                links[item[0]] = item[1]

    def article(item):
        url, title = item
        try:
            return parse_news(fetch(url), url, title, config, roster, today), None
        except Exception as exc:
            return (None, None), {'source': url, 'error': type(exc).__name__}

    # Bounded low concurrency; only metadata/title/link, no image downloads.
    selected = list(links.items())[:config['maxArticles']]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for (url, title), ((record, reason), error) in zip(selected, pool.map(article, selected)):
            if error:
                report['errors'].append(error)
            elif record:
                articles.append(record)
            else:
                report['candidates'].append({'kind': 'news', 'title': title, 'sourceUrl': url, 'reason': reason})
    manual_papers = [p for g in read_json(DATA / 'publications.json') for p in g['items']]
    news = read_json(DATA / 'news.json')
    manual_news = [*news['news'], *news['papers']]
    old_papers = [p for p in read_json(DATA / 'auto-publications.json', []) if p['id'] not in retracted]
    new_papers = merge_records(old_papers, papers, manual_papers, 'papers', config, today)
    new_news = merge_records(read_json(DATA / 'auto-news.json', []), articles, manual_news, 'news', config, today)
    write_json(DATA / 'auto-publications.json', new_papers)
    write_json(DATA / 'auto-news.json', new_news)
    covered_students = sorted({s for p in papers for s in p['studentCoauthors']})
    report['studentCoauthorMatches'] = covered_students
    report['studentsWithoutContextMatch'] = sorted({s['name'] for s in roster['students']} - set(covered_students))
    report['counts'] = {'roster': len(report['rosterNames']), 'apiWorks': len(works), 'verifiedPapers': len(papers),
                        'autoPapers': len(new_papers), 'checkedArticles': len(selected), 'autoNews': len(new_news)}
    report['coverageNote'] = 'Student aliases are used only with a verified teacher and Qinghai affiliation. Unmatched students are still searched in college news. No standalone student identity is inferred from a name.'
    write_json(Path(args.report), report)
    print(json.dumps(report['counts'], ensure_ascii=False))
    if report['errors']:
        print(f"{len(report['errors'])} source errors; existing entries retained. See sync report.", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
