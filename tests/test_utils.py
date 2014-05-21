"""Tests for the Texcavator utility functions"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")

from nose.tools import assert_equals
from testfixtures import compare

import texcavator.utils as utils


def test_json_error_message():
    response = utils.json_response_message('error', 'test')

    compare(response.content, '{"status": "error", "msg": "test"}')
    assert_equals(response.status_code, 200)


def test_json_ok_message():
    response = utils.json_response_message('ok', 'test', {'p': 'test'})

    compare(response.content, '{"status": "ok", "msg": "test", "p": "test"}')
    assert_equals(response.status_code, 200)
