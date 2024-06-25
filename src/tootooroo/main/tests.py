from django.test import TestCase
from django.urls import reverse, resolve
from main.views import top

class TopPageTest(TestCase):
    def test_top_page_returns_200_and_expected_title(self):
        response = self.client.get('/')
        self.assertContains(response, 'トゥットゥルー♪', status_code=200)

    def test_top_page_uses_expected_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'toot/top.html')

class TestSnippetURLs(TestCase):
    def test_top_url_resolves_to_top_view(self):
        url = reverse('top')  # Assuming 'top' is the name of the URL pattern for the top view
        resolver = resolve(url)
        self.assertEqual(resolver.func, top)

    # Add more tests for other URL patterns as needed

