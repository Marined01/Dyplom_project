from django.test import TestCase
from coursework.models import AccessGroup, Key, User


class CourseworkTestCase(TestCase):
    password = "test-pass-123"

    @classmethod
    def create_user(cls, email, *, is_staff=False):
        user = User.objects.create_user(
            email=email,
            name="Тест",
            surname="Користувач",
            password=cls.password,
        )
        if is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        return user

    @classmethod
    def create_key(cls, auditory, *, status="free", holder=None):
        return Key.objects.create(auditory=auditory, status=status, holder=holder)

    @classmethod
    def grant_group_access(cls, user, keys):
        group = AccessGroup.objects.create(name="Тестова група")
        group.keys.set(keys)
        user.access_groups.add(group)
        return group

    def login(self, user):
        return self.client.login(email=user.email, password=self.password)
