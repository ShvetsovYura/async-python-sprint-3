from datetime import datetime
import json
from unittest import TestCase

from utils import json_object_hook, EnhancedJsonEncoder


class TestUtils(TestCase):

    def test_json_object_hook(self):
        obj = {'created_at': '2022-12-12 16:25:14', 'text': 'test_text'}
        result = json_object_hook(obj)
        self.assertEqual({
            'created_at': datetime(2022, 12, 12, 16, 25, 14),
            'text': 'test_text',
        }, result)

    def test_EnhancedJsonEncoder(self):
        obj = {
            'created_at': datetime(2022, 12, 12, 16, 25, 14),
            'text': 'test_text',
        }

        result = json.dumps(obj, cls=EnhancedJsonEncoder)

        self.assertEqual('{"created_at": "2022-12-12 16:25:14", "text": "test_text"}', result)
