from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

POST_CREATE = reverse('posts:post_create')


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='SomeUsername')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.one_more_group = Group.objects.create(
            title='Еще один заголовок',
            slug='one_more_test_slug',
            description='Еще одно тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый псто',
            author=cls.user,
            group=cls.group)

        cls.POST_EDIT = reverse('posts:post_edit', args={cls.post.id})
        cls.POST_DETAIL = reverse('posts:post_detail', args={cls.post.id})
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
        posts_before = set(Post.objects.all())
        self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        new_post_list = list(posts_after.difference(posts_before))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(len(new_post_list), 1)
        self.assertEqual(new_post_list[0].text, self.post.text)
        self.assertEqual(new_post_list[0].group.id, self.group.id)

    def test_post_edit(self):
        '''Редактирование поста'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.one_more_group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        post_list = Post.objects.all()
        # import pdb; pdb.set_trace()
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(len(post_list), 1)
        self.assertEqual(post_list[0].text, 'Измененный пост')
        self.assertEqual(post_list[0].group.id, self.one_more_group.id)
        self.assertEqual(post_list[0].author, self.post.author)

    def test_create_post_has_correct_form(self):
        '''Шаблон создания поста сформирован с правильным контекстом'''
        response_create = self.authorized_client.get(POST_CREATE)
        response_edit = self.authorized_client.get(self.POST_EDIT)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_create = response_create.context.get(
                    'form').fields.get(value)
                form_field_edit = response_edit.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_create, expected)
                self.assertIsInstance(form_field_edit, expected)
