from posts.forms import PostForm
from posts.models import Post, Group, User
from django.test import Client, TestCase
from django.urls import reverse


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SomeUsername')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый псто',
            author=cls.user,
            group=cls.group)

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form = PostForm()

    def test_create_post(self):
        '''Создание поста'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый псто',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый псто',
                group=self.group.id
            ).exists()
        )

    def test_post_edit(self):
        '''Редактирование поста'''
        posts_count = Post.objects.count()
        post_id = self.post.pk
        form_data = {
            'text': 'Измененный пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args={self.post.pk})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_id, self.post.pk)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )