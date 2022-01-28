from http import HTTPStatus
from http.client import NOT_FOUND

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


MAIN_PAGE = reverse('posts:main_page')
CREATE = reverse('posts:post_create')
GROUP_LIST = reverse('posts:group_list', args=['test_slug'])
PROFILE = reverse('posts:profile', args=['SomeUsername'])
UNEXISTING = '/unexisting/'
LOGIN = reverse('users:login')
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND
CREATE_REDIRECT = f'{LOGIN}?next={CREATE}'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='SomeUsername')
        cls.another_user = User.objects.create(username='SomeAnotherUsername')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_EDIT_REDIRECT = f'{LOGIN}?next={cls.POST_EDIT}'

        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.another_user)

    def test_URLs(self):
        '''URLs availability test'''
        URLS = (
            (MAIN_PAGE, self.guest, OK),
            (MAIN_PAGE, self.author, OK),
            (GROUP_LIST, self.guest, OK),
            (PROFILE, self.guest, OK),
            (self.POST_DETAIL, self.guest, OK),
            (self.POST_EDIT, self.author, OK),
            (CREATE, self.author, OK),
            (UNEXISTING, self.author, NOT_FOUND),
            (self.POST_EDIT, self.guest, FOUND),
            (CREATE, self.guest, FOUND),
            (self.POST_EDIT, self.another, FOUND)
        )
        for url, client, status in URLS:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_edit_guest(self):
        '''Redirects test'''
        redirects = [
            [self.POST_EDIT, self.guest, self.POST_EDIT_REDIRECT],
            [CREATE, self.guest, CREATE_REDIRECT],
            [self.POST_EDIT, self.another, self.POST_DETAIL]
        ]
        # import pdb; pdb.set_trace()
        for url, client, redirected_url in redirects:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url), redirected_url)

    def test_urls_uses_correct_template(self):
        '''Tamplates test'''
        templates_url_names = {
            MAIN_PAGE: 'posts/index.html',
            GROUP_LIST: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            self.POST_DETAIL: 'posts/post_detail.html',
            self.POST_EDIT: 'posts/create_post.html',
            CREATE: 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(self.author.get(adress), template)
