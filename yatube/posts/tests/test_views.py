from django.contrib.auth import get_user_model
# from django.http import response
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

import datetime as dt

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
        cls.posts = []

        for id in range(13):
            post = Post.objects.create(
                id=id,
                text='Тестовый псто',
                author=cls.user,
                group=cls.group)
            cls.posts.append(post)

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        '''URL использует соответствующий шаблон'''
        templates_pages_names = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    args=['SomeUsername']): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=['3']): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=['3']): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_correct_context(self):
        '''Шаблон главной страницысформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:main_page'))
        first_object = response.context['page_obj'][0]
        post_pub_date_0 = first_object.pub_date.date()
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        # self.assertEqual(post_pub_date_0, dt.date.today())
        self.assertEqual(post_text_0, 'Тестовый псто')
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)

    def test_index_paginator_first_page(self):
        response = self.client.get(reverse('posts:main_page'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_paginator_second_page(self):
        response = self.client.get(reverse('posts:main_page') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_has_correct_context(self):
        '''Шаблон группы сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test_slug'}))
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        post_pub_date_0 = first_object.pub_date.date()
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        group_title_0 = second_object.title
        group_description_0 = second_object.description
        # self.assertEqual(post_pub_date_0, dt.date.today())
        self.assertEqual(post_text_0, 'Тестовый псто')
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(group_title_0, 'Тестовый заголовок')
        self.assertEqual(group_description_0, 'Тестовое описание')

    def test_group_list_paginator_first_page(self):
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_paginator_second_page(self):
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_has_correct_context(self):
        '''Шаблон профиля сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:profile',
                                                      args=['SomeUsername']))
        first_object = response.context['page_obj'][0]
        second_object = response.context['author']
        post_pub_date_0 = first_object.pub_date.date()
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = second_object.username
        #  self.assertEqual(post_pub_date_0, dt.date.today())
        self.assertEqual(post_text_0, 'Тестовый псто')
        self.assertEqual(post_author_0, 'SomeUsername')
        self.assertEqual(post_group_0, self.group)

    def test_author_paginator_first_page(self):
        response = self.client.get(reverse('posts:profile',
                                           args=['SomeUsername']))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_author_paginator_second_page(self):
        response = self.client.get(
            reverse('posts:profile',
                    args=['SomeUsername']) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail_has_correct_context(self):
        '''Шаблон поста сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    args=['3']))
        first_object = response.context['post']
        post_pub_date_0 = first_object.pub_date.date()
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        # self.assertEqual(post_pub_date_0, dt.date.today())
        self.assertEqual(post_text_0, 'Тестовый псто')
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)

    def test_create_post_has_correct_form(self):
        '''Шаблон создания поста сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_has_correct_form(self):
        '''Шаблон изменения поста сформирован с правильным контекстом'''
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    args=['3']))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_to_the_right_group(self):
        '''Пост попадает в правильную группу'''
        response = self.authorized_client.get(reverse('posts:main_page'))
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)
