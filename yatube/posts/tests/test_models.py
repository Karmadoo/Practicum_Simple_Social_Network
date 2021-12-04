from django.contrib.auth import get_user_model
from django.test import TestCase

from . .models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        '''Checking that models has correct __str__ method.'''
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_name = group.title
        expected_post_name = post.text
        self.assertEqual(expected_group_name, str(group))
        self.assertEqual(expected_post_name, str(post))
