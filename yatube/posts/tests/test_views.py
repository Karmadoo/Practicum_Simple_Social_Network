from posts.settings import (
    POSTS_PER_PAGE, POSTS_SECOND_PAGE
)


from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


MAIN_PAGE = reverse('posts:main_page')
MAIN_PAGE_PAGINATOR_SECOND = MAIN_PAGE + '?page=2'
GROUP_LIST = reverse('posts:group_list', args=['test_slug'])
GROUP_LIST_PAGINATOR_SECOND = f'{GROUP_LIST}?page=2'
ANOTHER_GROUP_LIST = reverse(
    'posts:group_list', args=['another_test_slug']
)
PROFILE = reverse('posts:profile', args=['SomeUsername'])
PROFILE_PAGINATOR_SECOND = f'{PROFILE}?page=2'
PAGE_START = 0
PAGE_END = 9


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
        cls.one_more_group = Group.objects.create(
            title='Другой тестовый заголовок',
            slug='another_test_slug',
            description='Еще тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Test post',
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail', args=[cls.post.pk]
        )
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.post.pk])

        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)

    def test_pages_has_correct_context(self):
        '''The page tamplates withs the right context'''
        urls = {
            MAIN_PAGE: 'page_obj',
            GROUP_LIST: 'page_obj',
            PROFILE: 'page_obj',
            self.POST_DETAIL: 'post',
        }
        for url, context_name in urls.items():
            with self.subTest(url=url):
                response = self.author.get(url)
                if context_name == 'page_obj':
                    post_list = response.context['page_obj']
                    self.assertEqual(len(post_list), 1)
                    checking_post = post_list[0]
                else:
                    checking_post = response.context['post']
                self.assertEqual(checking_post.text, self.post.text)
                self.assertEqual(checking_post.author, self.post.author)
                self.assertEqual(checking_post.group, self.post.group)
                self.assertEqual(checking_post.id, self.post.id)

    def test_group_list_has_correct_context(self):
        '''Group template with the right context'''
        response = self.author.get(GROUP_LIST)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.pk, self.group.pk)

    def test_profile_has_correct_context(self):
        '''Profile tamplate with the right context'''
        response = self.author.get(PROFILE)
        self.assertEqual(
            response.context['author'].username, self.user.username
        )

    def test_post_to_the_right_group(self):
        '''Post in the right group'''
        response = self.author.get(ANOTHER_GROUP_LIST)
        group_posts = response.context['page_obj']
        self.assertNotIn(self.post, group_posts)


class PaginatorTest(TestCase):
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
        for i in range(POSTS_PER_PAGE + POSTS_SECOND_PAGE):
            cls.posts.append(Post(
                text=f'Тестовый псто {i}',
                author=cls.user,
                group=cls.group,
            ))
        Post.objects.bulk_create(cls.posts)

        cls.guest = Client()

    def test_paginator(self):
        urls = {
            MAIN_PAGE: POSTS_PER_PAGE,
            MAIN_PAGE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            GROUP_LIST: POSTS_PER_PAGE,
            GROUP_LIST_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            PROFILE: POSTS_PER_PAGE,
            PROFILE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
        }
        for url, number in urls.items():
            with self.subTest(url=url):
                response = self.guest.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), number
                )
