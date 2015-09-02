import os

from nose.tools import assert_equals

from services.es import single_document_word_cloud
from texcavator.settings import ES_INDEX, ES_DOCTYPE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")


def test_single_document_word_cloud_invalid_id():
    invalid_ids = (None, '', 'saisdf19ju2')

    for id in invalid_ids:
        res = single_document_word_cloud(ES_INDEX, ES_DOCTYPE, id)
        assert_equals(res.get('status'), 'error')

