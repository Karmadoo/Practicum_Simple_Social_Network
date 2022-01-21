import random


from posts.settings import (
    POSTS_PER_PAGE, POSTS_SECOND_PAGE, PAGE_START, PAGE_END
)


from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


MAIN_PAGE = reverse('posts:main_page')


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
        cls.GROUP_LIST = reverse('posts:group_list', args=[cls.group.slug])
        cls.ANOTHER_GROUP_LIST = reverse(
            'posts:group_list', args=[cls.one_more_group.slug]
        )
        cls.PROFILE = reverse('posts:profile', args=[cls.user.username])

        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый псто {i}',
                author=cls.user,
                group=cls.group,
                id=i,
            ))
        Post.objects.bulk_create(cls.posts)

        cls.random_post = random.choice(
            Post.objects.filter(id__range=(PAGE_START, PAGE_END))
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail', args=[cls.random_post.id]
        )
        cls.POST_EDIT = reverse('posts:post_edit', args=[cls.random_post.id])

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_has_correct_context(self):
        '''The page tamplates withs the right context'''
        urls = [
            MAIN_PAGE,
            self.GROUP_LIST,
            self.PROFILE,
            self.POST_DETAIL1,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                post_list = response.context['page_obj']
                for checking_post in post_list:
                    if checking_post.id == self.random_post.id:
                        return checking_post
                self.assertEqual(checking_post.text, self.random_post.text)
                self.assertEqual(checking_post.author, self.random_post.author)
                self.assertEqual(checking_post.group, self.random_post.group)
                self.assertEqual(checking_post.id, self.random_post.id)

    def test_paginators_first_page(self):
        urls = [MAIN_PAGE, self.GROUP_LIST, self.PROFILE]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_PER_PAGE
                )

    def test_paginators_second_page(self):
        urls = [MAIN_PAGE, self.GROUP_LIST, self.PROFILE]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_SECOND_PAGE
                )

    def test_group_list_has_correct_context(self):
        '''Шаблон группы сформирован с правильным контекстом'''
        response = self.authorized_client.get(self.GROUP_LIST)
        group_object = response.context['group']
        self.assertEqual(group_object.title, self.group.title)
        self.assertEqual(group_object.description, self.group.description)
        self.assertEqual(group_object.slug, self.group.slug)
        self.assertEqual(group_object.pk, self.group.pk)

    def test_profile_has_correct_context(self):
        '''Шаблон профиля сформирован с правильным контекстом'''
        response = self.authorized_client.get(self.PROFILE)
        self.assertEqual(
            response.context['author'].username, self.user.username
        )

    def test_post_to_the_right_group(self):
        '''Пост попадает в правильную группу'''
        response = self.authorized_client.get(self.ANOTHER_GROUP_LIST)
        group_object = response.context['page_obj']
        self.assertNotIn(self.random_post, group_object)
