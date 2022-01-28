from django.test import TestCase
from django.urls import reverse


USER = 'SomeUsername'
SLUG = 'test_slug'
POST_ID = 3


class PostURLTests(TestCase):

    def test_routes(self):
        route_list = (
            ('/', 'main_page'),
            ('/create/', 'post_create'),
            ('/group/test_slug/', 'group_list', SLUG),
            ('/profile/SomeUsername/', 'profile', USER),
            ('/posts/3/', 'post_detail', POST_ID),
            ('/posts/3/edit/', 'post_edit', POST_ID),
        )
        for route, url, *key in route_list:
            with self.subTest(route=route):
                response = reverse(f'posts:{url}', args=key)
                self.assertEqual(route, response)
