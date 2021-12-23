from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User

VERBOSE_NAMES = [
    {
        'text': 'Текст',
        'pub_date': 'Дата публикации',
        'author': 'Автор',
        'group': 'Группа'
    },
    {
        'text': 'Текст комментария',
        'post': 'Пост комментария',
        'author': 'Автор комментария'
    },
    {
        'title': 'Заголовок',
        'slug': 'Слаг адреса',
        'description': 'Описание'
    },
    {
        'user': 'Подписчик',
        'author': 'Автор, на которого подписались'
    }
]

HELP_TEXTS = [
    {
        'text': 'Введите текст поста',
        'group': 'Выберите группу',
    },
    {
        'text': 'Введите текст комментария'
    }
]


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.models = [  # Сначала идут те, кому нужно проверить help_text
            cls.post,
            cls.comment,
            cls.group,
            cls.follow
        ]
        cls.expected_str = [
            cls.post.text[:15],
            cls.comment.text[:15],
            cls.group.title,
            str(cls.user)
        ]

    def test_models_str(self):
        """__str__ моделей совпадает с ожидаемым."""
        for i in range(len(self.models)):
            self.assertEqual(self.expected_str[i], str(self.models[i]))

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for i in range(len(self.models)):
            for field, expected_value in VERBOSE_NAMES[i].items():
                with self.subTest(field=field):
                    self.assertEqual(
                        self.models[i]._meta.get_field(field).verbose_name,
                        expected_value,
                    )

    def test_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        for i in range(0, 1):
            for field, expected_value in HELP_TEXTS[i].items():
                with self.subTest(field=field):
                    self.assertEqual(
                        self.models[i]._meta.get_field(field).help_text,
                        expected_value,
                    )
