import json
from pathlib import Path
import unittest

from audit_publications import verified_auto
from publication_metadata import metadata, normalize

DATA = Path(__file__).resolve().parents[1] / 'src/data'


class PublicationMetadataTests(unittest.TestCase):
    def test_manual_and_approved_records_have_verified_source_and_venue(self):
        manual = json.loads((DATA / 'publications.json').read_text(encoding='utf-8'))
        automatic = json.loads((DATA / 'auto-publications.json').read_text(encoding='utf-8'))
        saved = json.loads((DATA / 'publication-metadata.json').read_text(encoding='utf-8'))
        # Pending automatic records are retained for review but not displayed.
        for paper in [p for g in manual for p in g['items']] + [p for p in automatic if p['id'] in saved]:
            with self.subTest(id=paper['id']):
                verified = saved[paper['id']]
                for field in ('title', 'venue', 'label', 'doi', 'verification', 'checkedOn'):
                    self.assertTrue(verified[field])
                self.assertTrue(verified['link'].startswith('https://'))

    def test_edtc_alias_has_tpds_source(self):
        saved = json.loads((DATA / 'publication-metadata.json').read_text(encoding='utf-8'))
        record = saved['manual:66d3bf7cbfa8d1e21da2']
        self.assertEqual(record['label'], 'IEEE TPDS')
        self.assertEqual(record['doi'], '10.1109/tpds.2025.3627974')

    def test_identical_titles_from_different_authors_are_not_approved(self):
        paper = {'title': 'PCIAS', 'doi': 'https://doi.org/10.1145/3287055', 'authors': ['Zeshui Li']}
        result = {'exact': True, 'record': {'DOI': '10.1145/3287055', 'container-title': ['Journal'],
                                           'author': [{'given': 'Someone', 'family': 'Else'}]}}
        self.assertFalse(verified_auto(paper, result))
        result['record']['author'] = [{'given': 'Zeshui', 'family': 'Li'}]
        self.assertTrue(verified_auto(paper, result))
        result['record']['DOI'] = '10.1145/3287057'
        self.assertFalse(verified_auto(paper, result))

    def test_similar_title_is_held_for_review(self):
        paper = {'doi': 'https://doi.org/10.1/example', 'authors': ['First Author']}
        result = {'exact': False, 'record': {'DOI': '10.1/example', 'container-title': ['Journal'],
                                            'author': [{'given': 'First', 'family': 'Author'}]}}
        self.assertFalse(verified_auto(paper, result))

    def test_book_volume_is_used_instead_of_series(self):
        record = metadata({'DOI': '10.1/example', 'title': ['Example'], 'type': 'book-chapter',
                           'container-title': ['Lecture Notes in Computer Science', 'Euro-Par 2026: Parallel Processing']}, '2026-10-10')
        self.assertEqual(record['label'], 'Euro-Par')

    def test_title_normalization_decodes_html_before_stripping_tags(self):
        self.assertEqual(normalize('&lt;italic&gt;EnReal&lt;/italic&gt;: Example'), normalize('EnReal: Example'))


if __name__ == '__main__':
    unittest.main()
