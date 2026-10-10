import copy
from datetime import date
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from sync_content import (CollegeHTML, fetch_works, merge_records, news_links,
                          paper_record, parse_news, ocr_news_members)
from news_ocr import CollegeImageRedirect, NewsImageLimit, image_url_allowed
import sync_content

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


class PapersOnlyTests(unittest.TestCase):
    def test_default_run_never_fetches_or_rewrites_news(self):
        original_read = sync_content.read_json

        def read(path, *args):
            self.assertNotIn(path.name, ('news.json', 'auto-news.json'))
            return original_read(path, *args)

        with patch('sys.argv', ['sync_content.py']), \
             patch.object(sync_content, 'read_json', side_effect=read), \
             patch.object(sync_content, 'fetch_works', return_value=[]), \
             patch.object(sync_content, 'fetch', side_effect=AssertionError('College must not be fetched')), \
             patch.object(sync_content, 'NewsOCR', side_effect=AssertionError('OCR must not start')), \
             patch.object(sync_content, 'write_json') as write:
            self.assertEqual(sync_content.main(), 0)
        self.assertEqual([call.args[0].name for call in write.call_args_list],
                         ['auto-publications.json', 'sync-report.json'])
        report = write.call_args_list[-1].args[1]
        self.assertFalse(report['newsEnabled'])
        self.assertEqual(report['counts']['checkedArticles'], 0)


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

    def test_only_article_images_are_collected(self):
        parser = CollegeHTML()
        parser.feed('<nav><img src="logo.jpg"></nav><div class="article"><img src="poster.jpg"></div><footer><img src="qr.jpg"></footer>')
        self.assertEqual(parser.images, ['poster.jpg'])

    def test_low_confidence_name_and_common_student_not_published(self):
        lines = [{'text': '青海大学学术交流', 'score': 0.99}, {'text': '边浩东老师参加', 'score': 0.72}]
        self.assertFalse(ocr_news_members(lines, CONFIG, ROSTER)[1])
        self.assertFalse(ocr_news_members([{'text': '青海大学李博参加活动', 'score': 0.99}], CONFIG, ROSTER)[1])

    def test_school_context_and_exact_names_required(self):
        self.assertFalse(ocr_news_members([{'text': '边浩东到访其他学校', 'score': 0.99}], CONFIG, ROSTER)[1])
        self.assertFalse(ocr_news_members([{'text': '青海大学边浩冬指导比赛', 'score': 0.99}], CONFIG, ROSTER)[1])
        names, verified = ocr_news_members([{'text': '青海大学边浩东指导竞赛', 'score': 0.99}], CONFIG, ROSTER)
        self.assertTrue(verified)
        self.assertEqual(names, ['边浩东'])

    def test_english_teacher_names_in_research_posters(self):
        lines = [{'text': '青海大学联合团队', 'score': 0.99},
                 {'text': 'Guojing Zhang、Xiaoying Wang、Jianqiang Huang', 'score': 0.99}]
        names, verified = ocr_news_members(lines, CONFIG, ROSTER)
        self.assertTrue(verified)
        self.assertEqual(names, ['张国晶', '王晓英', '黄建强'])

    def test_ocr_publishes_original_metadata_without_copying_body(self):
        class FakeOCR:
            def read(self, url):
                return [{'text': '青海大学边浩东指导竞赛', 'score': 0.99}]
        html = self.page('<img src="../images/2026-03/poster.jpg">')
        result, _ = parse_news(html, 'https://cs.qhu.edu.cn/xkjs/a.htm', '活动', CONFIG, ROSTER, TODAY, FakeOCR())
        self.assertEqual(result['title'], '学术交流')
        self.assertEqual(result['date'], '2026-03-01')
        self.assertEqual(result['verification'], 'article-image-ocr')
        self.assertNotIn('body', result)
        self.assertEqual(result['evidenceImages'], ['https://cs.qhu.edu.cn/images/2026-03/poster.jpg'])

    def test_no_external_images_are_downloaded(self):
        for url in ['https://evil.example/images/a.jpg', 'http://cs.qhu.edu.cn/images/a.jpg',
                    'https://cs.qhu.edu.cn:8000/images/a.jpg', 'https://cs.qhu.edu.cn/images/a.svg',
                    'https://cs.qhu.edu.cn/avatar.jpg', 'file:///tmp/a.jpg']:
            self.assertFalse(image_url_allowed(url))
        self.assertTrue(image_url_allowed('https://cs.qhu.edu.cn/images/2026-03/a.jpg'))

    def test_large_images_remain_candidates(self):
        class LargeImageOCR:
            def read(self, url):
                raise NewsImageLimit('Too large')
        result, reason = parse_news(self.page('<img src="../images/2026-03/poster.jpg">'),
                                    'https://cs.qhu.edu.cn/xkjs/a.htm', '活动', CONFIG, ROSTER, TODAY, LargeImageOCR())
        self.assertIsNone(result)
        self.assertEqual(reason, 'image-too-large-for-ocr')

    def test_external_redirect_is_blocked_before_request(self):
        with self.assertRaises(ValueError):
            CollegeImageRedirect().redirect_request(None, None, 302, 'redirect', {}, 'https://evil.example/images/a.jpg')


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
