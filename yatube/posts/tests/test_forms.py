import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TEST_USERNAME = 'auth'
TEST_SLUG = 'test-slug'
TEST_COMMENT_TEXT = 'Новый комментарий'
CREATED_POST_TEXT = 'Новый пост'
EDITED_POST_TEXT = 'Изменённый пост'

POST_DETAIL = 'posts:post_detail'
PROFILE = 'posts:profile'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'
POST_ADD_COMMENT = 'posts:add_comment'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Редирект и добавление в БД после создания нового поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': CREATED_POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE,
            kwargs={'username': TEST_USERNAME}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=CREATED_POST_TEXT,
            ).exists()
        )

    def test_post_edit(self):
        """Редирект и изменения в БД после редактирования поста."""
        form_data = {
            'text': EDITED_POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_EDIT, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            POST_DETAIL,
            kwargs={'post_id': self.post.id}
        ))
        self.assertTrue(
            Post.objects.filter(
                text=EDITED_POST_TEXT,
            ).exists()
        )

    def test_image_saved(self):
        """Редирект и добавление в БД после отправки формы с картинкой."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': CREATED_POST_TEXT,
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE,
            kwargs={'username': TEST_USERNAME}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif',
            ).exists()
        )

    def test_comment_saved(self):
        """Редирект и добавление в БД после отправления комментария."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': TEST_COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            reverse(
                POST_ADD_COMMENT,
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            POST_DETAIL,
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=TEST_COMMENT_TEXT,
            ).exists()
        )
