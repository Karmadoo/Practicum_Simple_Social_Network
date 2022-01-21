from http import HTTPStatus


from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post, Group, User


MAIN_PAGE = reverse('posts:main_page')
CREATE = reverse('posts:post_create')
UNEXISTING = '/unexisting/'
LOGIN = reverse('users:login')


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

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_URLs(self):
        '''URLs availability test'''
        URLS = (
            (MAIN_PAGE, self.guest_client, HTTPStatus.OK),
            (self.GROUP_LIST, self.guest_client, HTTPStatus.OK),
            (self.PROFILE, self.guest_client, HTTPStatus.OK),
            (self.POST_DETAIL, self.guest_client, HTTPStatus.OK),
            (self.POST_EDIT, self.authorized_client, HTTPStatus.OK),
            (CREATE, self.authorized_client, HTTPStatus.OK),
            (UNEXISTING, self.authorized_client, HTTPStatus.NOT_FOUND),
            (self.POST_EDIT, self.guest_client, HTTPStatus.FOUND),
            (CREATE, self.guest_client, HTTPStatus.FOUND),
        )
        for url, client, status in URLS:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_edit_guest(self):
        # проверка изменения поста
        response = self.guest_client.get(self.POST_EDIT)
        self.assertRedirects(response, f'{LOGIN}?next={self.POST_EDIT}')

    def test_post_create_guest(self):
        # проверка создания поста
        response = self.guest_client.get(CREATE)
        self.assertRedirects(response, f'{LOGIN}?next={CREATE}')

    def test_urls_uses_correct_template(self):
        # адреса используют корректный шаблон
        templates_url_names = {
            MAIN_PAGE: 'posts/index.html',
            self.GROUP_LIST: 'posts/group_list.html',
            self.PROFILE: 'posts/profile.html',
            self.POST_DETAIL: 'posts/post_detail.html',
            self.POST_EDIT: 'posts/create_post.html',
            CREATE: 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
