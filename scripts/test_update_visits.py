from datetime import date
import unittest
from update_visits import advance


class VisitCounterTests(unittest.TestCase):
    def test_daily_range_and_repeat_run(self):
        data = {'count': 0, 'lastIncrementDate': '2026-10-10', 'mode': 'static'}
        updated = advance(data, date(2026, 10, 11), lambda upper: upper - 1)
        self.assertEqual(updated['count'], 5)
        self.assertEqual(advance(updated, date(2026, 10, 11)), updated)

    def test_strictly_over_4000_switches_to_three_days(self):
        data = {'count': 4000, 'lastIncrementDate': '2026-10-10'}
        updated = advance(data, date(2026, 10, 11), lambda upper: upper - 1)
        self.assertEqual(updated['count'], 4005)
        self.assertEqual(advance(updated, date(2026, 10, 13)), updated)
        self.assertEqual(advance(updated, date(2026, 10, 14), lambda upper: upper - 1)['count'], 4008)

    def test_zero_increment_still_consumes_eligible_day(self):
        data = {'count': 4001, 'lastIncrementDate': '2026-10-10'}
        updated = advance(data, date(2026, 10, 13), lambda upper: 0)
        self.assertEqual(updated['count'], 4001)
        self.assertEqual(updated['lastIncrementDate'], '2026-10-13')


if __name__ == '__main__':
    unittest.main()
