from django.test import Client, TestCase

from ..models import Group, Post, User

TEST_SLUG = 'test-slug'
TEST_POST_ID = 1
TEST_USERNAME = 'auth'
TEST_ADRESS = '/test_adress/'

INDEX_URL = '/'
POST_CREATE_URL = '/create/'
GROUP_URL = f'/group/{TEST_SLUG}/'
POST_DETAIL_URL = f'/posts/{TEST_POST_ID}/'
PROFILE_URL = f'/profile/{TEST_USERNAME}/'
POST_EDIT_URL = f'/posts/{TEST_POST_ID}/edit/'
ADD_COMMENT_URL = f'/posts/{TEST_POST_ID}/comment/'

TEMPLATES = {
    INDEX_URL: 'posts/index.html',
    POST_CREATE_URL: 'posts/create_post.html',
    GROUP_URL: 'posts/group_list.html',
    POST_DETAIL_URL: 'posts/post_detail.html',
    PROFILE_URL: 'posts/profile.html',
    POST_EDIT_URL: 'posts/create_post.html'
}

LOGIN_REDIRECT = f'/{TEST_USERNAME}/login/?next='
REDIRECTS = {
    POST_CREATE_URL: f'{LOGIN_REDIRECT}{POST_CREATE_URL}',
    POST_EDIT_URL: f'{LOGIN_REDIRECT}{POST_EDIT_URL}',
    ADD_COMMENT_URL: f'{LOGIN_REDIRECT}{ADD_COMMENT_URL}'
}


class PostURLTests(TestCase):
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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in TEMPLATES.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_redirects_anonymous(self):
        """Переадресация для неавторизованного пользователя."""
        for adress, redirect in REDIRECTS.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_adress_existance(self):
        """Доступность страниц."""
        for adress in TEMPLATES.keys():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_adress_not_found(self):
        """Возвращение 404 при несуществующей странице."""
        response = self.authorized_client.get(TEST_ADRESS)
        self.assertEqual(response.status_code, 404)
