# Тести доступу (access.py).
from coursework.access import user_can_access_key, user_has_any_access
from coursework.tests.base import CourseworkTestCase


class AccessTests(CourseworkTestCase):
    def setUp(self):
        self.staff = self.create_user("staff@uni.ua", is_staff=True)
        self.user = self.create_user("user@uni.ua")
        self.key = self.create_key("101")

    def test_staff_can_access_any_key(self):
        # is_staff має доступ до будь-якої аудиторії
        self.assertTrue(user_can_access_key(self.staff, self.key))

    def test_new_user_has_no_access(self):
        # Звичайний користувач без груп не бачить жодного ключа
        self.assertFalse(user_has_any_access(self.user))
        self.assertFalse(user_can_access_key(self.user, self.key))

    def test_group_opens_access(self):
        # Якщо адмін додав користувача в групу, з’являється доступ
        self.grant_group_access(self.user, [self.key])

        self.assertTrue(user_has_any_access(self.user))
        self.assertTrue(user_can_access_key(self.user, self.key))
