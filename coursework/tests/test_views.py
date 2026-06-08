# HTTP-тести (django.test.Client).
# Client надсилає запити на URL так, ніби це браузер.
# follow=True — йти за редіректом і дивитись фінальну відповідь.

from django.urls import reverse
from coursework.models import Key_requests
from coursework.tests.base import CourseworkTestCase


class SimpleViewTests(CourseworkTestCase):
    def setUp(self):
        self.user = self.create_user("user@uni.ua")
        self.allowed_key = self.create_key("101", status="free")
        self.other_key = self.create_key("999", status="free")
        self.grant_group_access(self.user, [self.allowed_key])

    def test_home_requires_login(self):
        # Головна сторінка доступна лише після входу
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_take_request_blocked_without_access(self):
        # Без доступу до аудиторії запит на ключ не створюється
        self.login(self.user)
        url = reverse("take_key_request", args=[self.other_key.id])
        response = self.client.post(url, follow=True)

        self.assertContains(response, "немає доступу")
        self.other_key.refresh_from_db()
        self.assertEqual(self.other_key.status, "free")

    def test_take_request_works_with_access(self):
        # З доступом запит створюється, ключ переходить pendng
        self.login(self.user)
        url = reverse("take_key_request", args=[self.allowed_key.id])
        response = self.client.post(url, follow=True)

        self.assertContains(response, "надіслано")
        self.allowed_key.refresh_from_db()
        self.assertEqual(self.allowed_key.status, "pending")
        self.assertTrue(
            Key_requests.objects.filter(user=self.user, key=self.allowed_key).exists()
        )

    def test_free_keys_page_hides_inaccessible_rooms(self):
        # у free_keys лише ті, до яких є доступ
        self.login(self.user)
        response = self.client.get(reverse("free_keys"))

        self.assertContains(response, "101")
        self.assertNotContains(response, "999")
