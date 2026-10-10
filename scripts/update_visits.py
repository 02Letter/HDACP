"""Update the temporary static counter, never more than once per eligible day."""
from datetime import date, datetime
import json
from pathlib import Path
from secrets import randbelow
from zoneinfo import ZoneInfo

PATH = Path(__file__).resolve().parents[1] / 'src/data/visits.json'


def advance(data, today, random=randbelow):
    previous = date.fromisoformat(data['lastIncrementDate'])
    count = data['count']
    interval = 3 if count > 4000 else 1
    if (today - previous).days < interval:
        return data
    return {**data, 'count': count + random(4 if count > 4000 else 6),
            'lastIncrementDate': today.isoformat(), 'mode': 'static'}


if __name__ == '__main__':
    data = json.loads(PATH.read_text(encoding='utf-8'))
    updated = advance(data, datetime.now(ZoneInfo('Asia/Shanghai')).date())
    if updated != data:
        PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Static counter:', updated['count'])
