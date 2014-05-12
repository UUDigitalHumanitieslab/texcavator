import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texcavator.settings")

from nose.tools import assert_equals

from services.views import daterange2dates
from texcavator.settings import TEXCAVATOR_DATE_RANGE

def test_daterange2dates():
    assert_equals(daterange2dates(TEXCAVATOR_DATE_RANGE), 
                  {'lower': '1850-01-01', 'upper':'1990-12-31'})
   
    # First date after second date
    assert_equals(daterange2dates("19901231,18500101"),
                  {'lower': '1850-01-01', 'upper':'1990-12-31'})

    # Input single date
    assert_equals(daterange2dates("19901231"),
                  {'lower': '1850-01-01', 'upper':'1990-12-31'})

    # Empty input
    assert_equals(daterange2dates(""),
                  {'lower': '1850-01-01', 'upper':'1990-12-31'})
