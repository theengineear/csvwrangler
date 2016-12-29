import os

from django.urls import reverse
from rest_framework.test import APITestCase


class CsvUploadTest(APITestCase):

    expected_result = {'eagle': 34, 'smith': 27, 'lee': 3}

    def get_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

    def test_upload_simple(self):
        # Params are well-defined and file has no empty values at all.
        url = reverse('csv-upload')
        with open(self.get_path('file0.csv')) as f:
            body = {'group': 'last_name', 'aggregate': 'count', 'file': f}
            response = self.client.post(url, body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.expected_result)

    def test_upload_padding(self):
        # Params are well-defined but some unused values may be blank.
        url = reverse('csv-upload')
        with open(self.get_path('file1.csv')) as f:
            body = {'group': 'last_name', 'aggregate': 'count', 'file': f}
            response = self.client.post(url, body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.expected_result)

    def test_upload_missing(self):
        # Params are well-defined but some required values are blank.
        url = reverse('csv-upload')
        with open(self.get_path('file2.csv')) as f:
            body = {'group': 'last_name', 'aggregate': 'count', 'file': f}
            response = self.client.post(url, body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.expected_result)

    def test_upload_bad_group(self):
        # If you pick a group value that's not in the file, fail gracefully.
        url = reverse('csv-upload')
        with open(self.get_path('file2.csv')) as f:
            body = {'group': 'foobar', 'aggregate': 'count', 'file': f}
            response = self.client.post(url, body)
        expected_result = {
            u'detail': u"Group and aggregate must be in headers. "
                       u"Headers: ['', 'first_name', 'last_name', 'count', "
                       u"'', '', '']"
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_result)

    def test_upload_bad_aggregate(self):
        # If you pick an aggregate that's not in the file, fail gracefully.
        url = reverse('csv-upload')
        with open(self.get_path('file2.csv')) as f:
            body = {'group': 'last_name', 'aggregate': 'zipbaz', 'file': f}
            response = self.client.post(url, body)
        expected_result = {
            u'detail': u"Group and aggregate must be in headers. "
                       u"Headers: ['', 'first_name', 'last_name', 'count', "
                       u"'', '', '']"
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_result)

    def test_upload_bad_file(self):
        url = reverse('csv-upload')
        body = {'group': 'last_name', 'aggregate': 'count', 'file': 5}
        response = self.client.post(url, body)
        expected_result = {u'detail': u'File must be file-like.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_result)

    def test_upload_bad_file_content(self):
        url = reverse('csv-upload')
        with open(self.get_path('file3.csv')) as f:
            body = {'group': 'last_name', 'aggregate': 'count', 'file': f}
            response = self.client.post(url, body)
        expected_result = {
            u'detail': u"Group and aggregate must be in headers. "
                       u"Headers: ['this is not a csv file...']"
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_result)

    def test_upload_no_file(self):
        url = reverse('csv-upload')
        body = {'group': 'last_name', 'aggregate': 'count'}
        response = self.client.post(url, body)
        expected_result = {u'detail': u'File must be file-like.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_result)
