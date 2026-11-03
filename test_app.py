import io
import json
import os
import unittest
from unittest.mock import patch
import app

class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

class Tests(unittest.TestCase):
    def test_invalid_inputs(self):
        for value in ([], {}, {'specs': []}, {'name': 3}):
            with self.subTest(value=value), self.assertRaises(ValueError): app.validate(value)

    @patch.dict(os.environ, {'OPENAI_API_KEY':'test'})
    @patch('urllib.request.urlopen')
    def test_characteristics_copied_and_missing_reported(self, urlopen):
        output = {'seo_title':'Манометр', 'seo_description':'Описание', 'search_queries':['манометр','манометр купить','давление'], 'commercial_block':'Данных нет', 'missing_fields':[]}
        urlopen.return_value = Response(json.dumps({'choices':[{'message':{'content':json.dumps(output)}}]}).encode())
        result = app.generate(app.validate({'name':'Манометр', 'specs':{'диапазон':'0–1 МПа'}}))
        self.assertEqual(result['key_characteristics'], {'диапазон':'0–1 МПа'})
        self.assertIn('manufacturer: данных нет', result['missing_fields'])
        self.assertIn('review_notice', result)

    @patch.dict(os.environ, {'OPENAI_API_KEY':'test'})
    @patch('urllib.request.urlopen')
    def test_bad_model_response(self, urlopen):
        urlopen.return_value = Response(b'{"choices":[{"message":{"content":"not json"}}]}')
        with self.assertRaisesRegex(ValueError, 'Некорректный ответ'): app.generate(app.validate({'name':'Прибор'}))

if __name__ == '__main__': unittest.main()
