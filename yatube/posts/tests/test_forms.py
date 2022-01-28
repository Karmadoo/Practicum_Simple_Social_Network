from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

POST_CREATE = reverse('posts:post_create')
PROFILE = reverse('posts:profile', args={'SomeUsername'})


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
        '''Post creating'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'some text',
            'group': self.one_more_group.id,
        }
        posts_before = set(Post.objects.all())
        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        new_post_list = list(posts_after.difference(posts_before))
        new_post = new_post_list[0]
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(len(new_post_list), 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.user)
        self.assertRedirects(response, PROFILE)

    def test_post_edit(self):
        '''Post editing'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.one_more_group.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        # import pdb; pdb.set_trace()
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.author, self.post.author)

    def test_create_post_has_correct_form(self):
        '''Шаблон создания поста сформирован с правильным контекстом'''
        urls = [POST_CREATE, self.POST_EDIT]
        for i in urls:
            response = self.authorized_client.get(i)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get(
                        'form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
