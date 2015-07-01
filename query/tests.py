from django.test import TestCase

from .models import StopWord


class SimpleTest(TestCase):
    def test_serialization(self):
        """Tests the serialization of a StopWord
        """
        s = StopWord(word='test')
        self.assertEqual(s.get_stopword_dict(), {'id': s.id, 'user': '', 'query': '', 'word': s.word})

