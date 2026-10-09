import copy
from datetime import date
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlparse

from sync_content import (CollegeHTML, fetch_works, merge_records, news_links,
                          paper_record, parse_news)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config/content-sources.json').read_text(encoding='utf-8'))
ROSTER = json.loads((ROOT / 'src/data/team.json').read_text(encoding='utf-8'))
TODAY = date(2026, 10, 9)


def work():
    return {'id': 'https://openalex.org/W1', 'display_name': '<script>Test</script> research',
            'publication_date': '2026-03-01', 'type': 'article', 'doi': 'https://doi.org/10.1/test',
            'authorships': [{'author': {'id': 'https://openalex.org/A5003261630',
                                      'display_name': 'Haodong Bian', 'orcid': None},
                            'institutions': [{'id': 'https://openalex.org/I116265982'}]}]}


class AttributionTests(unittest.TestCase):
    def test_teacher_with_per_paper_affiliation(self):
        result, _ = paper_record(work(), CONFIG, ROSTER, TODAY)
        self.assertEqual(result['members'], ['边浩东'])

    def test_homonym_rejected_and_unrelated_coauthor_affiliation_not_enough(self):
        wrong = work()
        wrong['authorships'][0]['author']['id'] = 'https://openalex.org/A999'
        self.assertIsNone(paper_record(wrong, CONFIG, ROSTER, TODAY)[0])
        wrong = work()
        wrong['authorships'][0]['institutions'] = []
        wrong['authorships'].append({'author': {'id': 'https://openalex.org/A999', 'display_name': 'Someone'},
                                    'institutions': [{'id': 'https://openalex.org/I116265982'}]})
        self.assertIsNone(paper_record(wrong, CONFIG, ROSTER, TODAY)[0])

    def test_orcid_fragment_and_untrusted_link(self):
        record = work()
        record['authorships'][0]['author'].update(id=None, orcid='https://orcid.org/0000-0003-0907-288X')
        self.assertIsNotNone(paper_record(record, CONFIG, ROSTER, TODAY)[0])
        record['doi'] = 'javascript:alert(1)'
        self.assertIsNone(paper_record(record, CONFIG, ROSTER, TODAY)[0])

    def test_future_preprint_and_retraction(self):
        for field, value in [('publication_date', '2027-01-01'), ('type', 'preprint'), ('is_retracted', True)]:
            record = work()
            record[field] = value
            self.assertIsNone(paper_record(record, CONFIG, ROSTER, TODAY)[0])

    def test_student_is_only_a_contextual_coauthor(self):
        record = work()
        student = {'author': {'id': 'https://openalex.org/A2', 'display_name': 'Jiafan Jiang'},
                   'institutions': [{'id': 'https://openalex.org/I116265982'}]}
        record['authorships'].append(student)
        self.assertEqual(paper_record(record, CONFIG, ROSTER, TODAY)[0]['studentCoauthors'], ['姜佳凡'])
        record['authorships'] = [student]
        self.assertIsNone(paper_record(record, CONFIG, ROSTER, TODAY)[0])


class NewsTests(unittest.TestCase):
    def page(self, body):
        return '<nav>边浩东 王晓英</nav><h2>学术交流</h2><div>发布日期：2026-03-01</div><div class="article"><p>' + body + '</p></div><script>黄建强</script>'

    def test_navigation_and_scripts_do_not_attribute_news(self):
        result, reason = parse_news(self.page('其他团队'), 'https://cs.qhu.edu.cn/xzjl/a.htm', '交流', CONFIG, ROSTER, TODAY)
        self.assertIsNone(result)
        self.assertEqual(reason, 'insufficient-member-evidence')

    def test_body_matches_and_same_name_student_requires_context(self):
        self.assertIsNotNone(parse_news(self.page('边浩东参加学术交流'), 'https://cs.qhu.edu.cn/xzjl/a.htm', '', CONFIG, ROSTER, TODAY)[0])
        self.assertIsNone(parse_news(self.page('李博参加活动'), 'https://cs.qhu.edu.cn/xzjl/a.htm', '', CONFIG, ROSTER, TODAY)[0])

    def test_markup_change_raises_instead_of_publishing(self):
        with self.assertRaises(ValueError):
            parse_news('<title>Verify you are human</title>', 'https://cs.qhu.edu.cn/xzjl/a.htm', '', CONFIG, ROSTER, TODAY)

    def test_links_are_restricted_to_college_articles(self):
        page = '<a href="' + 'a' * 32 + '.htm">报道</a><a href="https://evil.example/' + 'b' * 32 + '.htm">外部</a>'
        self.assertEqual(len(news_links(page, 'https://cs.qhu.edu.cn/xzjl/index.htm')), 1)


class SyncTests(unittest.TestCase):
    def test_pagination_collects_every_page(self):
        pages = iter([{'results': [{'id': 'W1'}], 'meta': {'next_cursor': 'second'}},
                      {'results': [{'id': 'W2'}], 'meta': {'next_cursor': None}}])
        cursors = []
        def getter(url, **kwargs):
            cursors.append(parse_qs(urlparse(url).query)['cursor'][0])
            return next(pages)
        self.assertEqual([r['id'] for r in fetch_works('author.id:A1', getter)], ['W1', 'W2'])
        self.assertEqual(cursors, ['*', 'second'])

    def test_empty_source_retains_existing_and_manual_dedup_across_years(self):
        record, _ = paper_record(work(), CONFIG, ROSTER, TODAY)
        self.assertEqual(merge_records([record], [], [], 'papers', CONFIG, TODAY), [record])
        duplicate = {'content': '[Test] ' + record['title'] + '（SCI，CCF C）', 'link': ''}
        self.assertEqual(merge_records([record], [], [duplicate], 'papers', CONFIG, TODAY), [])

    def test_stable_order_and_no_double_insert(self):
        record, _ = paper_record(work(), CONFIG, ROSTER, TODAY)
        result = merge_records([record], [copy.deepcopy(record)], [], 'papers', CONFIG, TODAY)
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
