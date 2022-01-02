from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User



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
        
        cls.POST_CREATE = reverse('posts:post_create')
        cls.POST_EDIT = reverse('posts:post_edit', args = {cls.post.id})
        cls.POST_DETAIL = reverse('posts:post_detail', args = {cls.post.id})
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form = PostForm()

    def test_create_post(self):
        '''Создание поста'''
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        self.authorized_client.post(
            self.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.group.id
            ).exists()
        )

    def test_post_edit(self):
        '''Редактирование поста'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.POST_DETAIL
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )
