"""Tests for the Texcavator utility functions"""
import os

from nose.tools import assert_equals

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
