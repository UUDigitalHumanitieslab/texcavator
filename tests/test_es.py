import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")

from nose.tools import assert_equals

from services.es import single_document_word_cloud
from texcavator.settings import ES_INDEX_KONBIB, ES_INDEX_DOCTYPE_KONBIB

def test_single_document_word_cloud_invalid_id():
    invalid_ids = (None, '', 'saisdf19ju2')

    for id in invalid_ids:
        res = single_document_word_cloud(ES_INDEX_KONBIB, 
                                             ES_INDEX_DOCTYPE_KONBIB, 
                                             id)
    assert_equals(res.get('status'), 'error')
