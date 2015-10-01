"""Tests for the Texcavator utility functions"""
import os
from nose.tools import assert_equals

from django.conf import settings

import texcavator.utils as utils

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")


def test_json_error_message():
    response = utils.json_response_message('error', 'test')

    assert_equals(response.content, '{"status": "error", "msg": "test"}')
    assert_equals(response.status_code, 200)


def test_json_ok_message():
    response = utils.json_response_message('ok', 'test', {'p': 'test'})

    assert_equals(response.content, '{"status": "ok", "msg": "test", "p": "test"}')
    assert_equals(response.status_code, 200)


def test_chunks():
    results = [chunk for chunk in utils.chunks([], 100)]
    assert_equals(results, [])

    results = [chunk for chunk in utils.chunks(range(5), 1)]
    assert_equals(results, [[0], [1], [2], [3], [4]])

    results = [chunk for chunk in utils.chunks(range(5), 2)]
    assert_equals(results, [[0, 1], [2, 3], [4]])


def test_daterange2dates():
    assert_equals(utils.daterange2dates(settings.TEXCAVATOR_DATE_RANGE),
                  [{'lower': '1850-01-01', 'upper': '1990-12-31'}])

    # Input single date
    assert_equals(utils.daterange2dates("19901231"),
                  [{'lower': '1850-01-01', 'upper': '1990-12-31'}])

    # Empty input
    assert_equals(utils.daterange2dates(""),
                  [{'lower': '1850-01-01', 'upper': '1990-12-31'}])


def test_flip_dict():
    example = {'1': 'one', '2': 'two'}
    result = utils.flip_dict(example)
    assert_equals(result, {'one': '1', 'two': '2'})
