# Тести правил моделі Key.
# методи take_key і put_key — без HTTP, лише логіка в коді.
from coursework.tests.base import CourseworkTestCase


class KeyRulesTests(CourseworkTestCase):
    def setUp(self):
        self.user = self.create_user("user@uni.ua")

    def test_take_key_marks_room_as_taken(self):
        #після видачі ключ стає зайнятий
        key = self.create_key("201")
        key.take_key(self.user)

        key.refresh_from_db()
        self.assertEqual(key.status, "taken")
        self.assertEqual(key.holder, self.user)

    def test_put_key_marks_room_as_free(self):
        # Після повернення аудиторія вільна
        key = self.create_key("202", status="taken", holder=self.user)
        key.put_key()

        key.refresh_from_db()
        self.assertEqual(key.status, "free")
        self.assertIsNone(key.holder)

    def test_user_cannot_hold_more_than_four_keys(self):
        # Один користувач не може тримати більше 4 ключів
        for n in range(4):
            self.create_key(f"30{n}").take_key(self.user)

        fifth = self.create_key("305")
        with self.assertRaises(ValueError):
            fifth.take_key(self.user)
