from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class StringReversalTests(TestCase):
    def setUp(self):
        """Initialize test client and other test variables."""
        self.client = APIClient()
        self.reverse_url = reverse('ping')

    def test_reverse_simple_string(self):
        """Test basic string reversal functionality."""
        data = {'ping': 'hello'}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ping'], 'hello')
        self.assertEqual(response.data['pong'], 'olleh')

    def test_reverse_empty_string(self):
        """Test reversal of empty string."""
        data = {'ping': ''}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ping'], '')
        self.assertEqual(response.data['pong'], '')

    def test_reverse_special_characters(self):
        """Test string reversal with special characters."""
        data = {'ping': 'Hello, World! 123 @@'}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ping'], 'Hello, World! 123 @@')
        self.assertEqual(response.data['pong'], '@@ 321 !dlroW ,olleH')

    def test_reverse_unicode_characters(self):
        """Test string reversal with Unicode characters."""
        data = {'ping': '😊 Hello 世界'}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ping'], '😊 Hello 世界')
        self.assertEqual(response.data['pong'], '界世 olleH 😊')

    def test_missing_text_field(self):
        """Test error handling for missing text field."""
        data = {}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_non_string_input(self):
        """Test error handling for non-string input."""
        data = {'ping': 123}
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_text_too_long(self):
        """Test error handling for text exceeding maximum length."""
        data = {'ping': 'a' * 1025}  # Create string longer than 1024 characters
        response = self.client.post(self.reverse_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('1024 characters', response.data['error'])
