import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import NUM_OF_PAGES

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TEST_SLUG = 'test-slug'
TEST_USERNAME = 'test-user'
TEST_USERNAME_AUTHOR = 'test-author'

INDEX = 'posts:index'
POST_CREATE = 'posts:post_create'
GROUP_LIST = 'posts:group_list'
POST_DETAIL = 'posts:post_detail'
PROFILE = 'posts:profile'
POST_EDIT = 'posts:post_edit'
FOLLOW_INDEX = 'posts:follow_index'
PROFILE_FOLLOW = 'posts:profile_follow'
PROFILE_UNFOLLOW = 'posts:profile_unfollow'

TEMPLATES = [
    'posts/index.html',
    'posts/group_list.html',
    'posts/profile.html',
    'posts/post_detail.html',
    'posts/create_post.html',
    'posts/create_post.html'
]


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.author = User.objects.create_user(
            username=TEST_USERNAME_AUTHOR
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.reverses = [
            reverse(INDEX),  # 0
            reverse(GROUP_LIST, kwargs={'slug': TEST_SLUG}),  # 1
            reverse(PROFILE, kwargs={'username': TEST_USERNAME}),  # 2
            reverse(POST_DETAIL, kwargs={'post_id': cls.post.id}),  # 3
            reverse(POST_EDIT, kwargs={'post_id': cls.post.id}),  # 4
            reverse(POST_CREATE),  # 5
            reverse(
                PROFILE_FOLLOW,
                kwargs={'username': TEST_USERNAME_AUTHOR}
            ),  # 6
            reverse(
                PROFILE_UNFOLLOW,
                kwargs={'username': TEST_USERNAME_AUTHOR}
            ),  # 7
            reverse(
                PROFILE_FOLLOW,
                kwargs={'username': TEST_USERNAME}
            ),  # 8
            reverse(FOLLOW_INDEX)  # 9
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for i in range(len(TEMPLATES)):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertTemplateUsed(response, TEMPLATES[i])

    def test_correct_context(self):
        """На страницы, где есть пост, передаётся нужный контекст"""
        for i in range(0, 2):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertEqual(
                    response.context['page_obj'].object_list[0].text,
                    self.post.text
                )
        for i in range(3, 4):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertEqual(
                    response.context['post'].text,
                    self.post.text
                )

    def test_image_in_context(self):
        """На страницы картинка передаётся вместе с контекстом."""
        for i in range(0, 2):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertEqual(
                    response.context['page_obj'].object_list[0].image,
                    self.post.image
                )
        response = self.authorized_client.get(self.reverses[3])
        self.assertEqual(
            response.context['post'].image,
            self.post.image
        )

    def test_context_on_post_create(self):
        """На страницу создания нового поста передается нужный контекст."""
        response = self.authorized_client.get(self.reverses[5])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_is_on_post_detail(self):
        """Комментарий отображается на странице поста после добавления."""
        test_comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=self.user,
            post=self.post,
        )
        response = self.authorized_client.get(self.reverses[3])
        self.assertContains(response, test_comment.text)

    def test_cache_index(self):
        """Кэширование сохраняет контент на 20 секунд."""
        response = self.authorized_client.get(self.reverses[0])
        content = response.content
        Post.objects.all().delete()
        response_new = self.authorized_client.get(self.reverses[0])
        content_new = response_new.content
        self.assertEqual(content, content_new)

    def test_user_can_follow(self):
        """Возможность подписки."""
        self.authorized_client.post(self.reverses[6])
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_user_can_unfollow(self):
        """Возможность отписки."""
        self.authorized_client.post(self.reverses[7])
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_user_cant_follow_himself(self):
        """Пользователь не может подписаться сам на себя."""
        self.authorized_client.post(self.reverses[8])
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.user).exists()
        )

    def test_follow_index_for_follower(self):
        """Посты автора появляются в ленте тех, кто на него подписан."""
        post_for_follow = Post.objects.create(
            author=self.author,
            text='Пост для проверки подписок',
            group=self.group,
        )
        self.authorized_client.post(self.reverses[6])
        response = self.authorized_client.get(self.reverses[9])
        self.assertEqual(
            response.context['page_obj'].object_list[0].text,
            post_for_follow.text
        )

    def test_follow_index_for_not_follower(self):
        """Посты автора не появляются в ленте тех, кто на него не подписан."""
        self.authorized_client.post(self.reverses[7])
        response = self.authorized_client.get(self.reverses[9])
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_paginator_and_context_on_pages_with_paginator(self):
        """Паджинатор отображает 10 постов, передается нужный контекст."""
        for i in range(13):
            self.post = Post.objects.create(
                author=self.user,
                text='Тестовый пост',
                group=self.group,
            )
        for i in range(0, 2):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.client.get(self.reverses[i])
                self.assertEqual(len(
                    response.context['page_obj']),
                    NUM_OF_PAGES
                )
