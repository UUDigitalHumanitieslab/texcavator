import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")

from nose.tools import assert_equals

from services.es import single_document_word_cloud, daterange2dates
from texcavator.settings import ES_INDEX, ES_DOCTYPE, TEXCAVATOR_DATE_RANGE


def test_single_document_word_cloud_invalid_id():
    invalid_ids = (None, '', 'saisdf19ju2')

    for id in invalid_ids:
        res = single_document_word_cloud(ES_INDEX, ES_DOCTYPE, id)
        assert_equals(res.get('status'), 'error')


def test_daterange2dates():
    assert_equals(daterange2dates(TEXCAVATOR_DATE_RANGE),
                  {'lower': '1850-01-01', 'upper': '1990-12-31'})

    # First date after second date
    assert_equals(daterange2dates("19901231,18500101"),
                  {'lower': '1850-01-01', 'upper': '1990-12-31'})

    # Input single date
    assert_equals(daterange2dates("19901231"),
                  {'lower': '1850-01-01', 'upper': '1990-12-31'})

    # Empty input
    assert_equals(daterange2dates(""),
                  {'lower': '1850-01-01', 'upper': '1990-12-31'})
