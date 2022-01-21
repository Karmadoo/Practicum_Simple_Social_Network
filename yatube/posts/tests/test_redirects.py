from django.test import TestCase
from django.urls import reverse


from posts.models import Post, Group, User


MAIN_PAGE = reverse('posts:main_page')
CREATE = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='SomeUsername')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.GROUP_LIST = reverse('posts:group_list', args=[cls.group.slug])
        cls.PROFILE = reverse('posts:profile', args=[cls.user.username])
        cls.post = Post.objects.create(
            pk='3',
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.pk])

    def test_routes(self):
        route_list = {
            '/': MAIN_PAGE,
            '/create/': CREATE,
            '/group/test_slug/': self.GROUP_LIST,
            '/profile/SomeUsername/': self.PROFILE,
            '/posts/3/': self.POST_DETAIL,
            '/posts/3/edit/': self.POST_EDIT,
        }
        for route, url in route_list.items():
            with self.subTest(route=route):
                self.assertEqual(route, url)
