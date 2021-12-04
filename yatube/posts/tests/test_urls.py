from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


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
        cls.post = Post.objects.create(
            pk='3',
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_abouth_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_abouth_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        # проверка создания группы
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        # проверка профиля
        response = self.guest_client.get('/profile/SomeUsername/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        # проверка поста
        response = self.guest_client.get('/posts/3/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        # проверка изменения поста
        response = self.authorized_client.get('/posts/3/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_create(self):
        # проверка создания поста
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        # проверка изменения поста
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        # адреса используют корректный шаблон
        templates_url_names = {
            '/': 'posts/index.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/SomeUsername/': 'posts/profile.html',
            '/posts/3/': 'posts/post_detail.html',
            '/posts/3/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
