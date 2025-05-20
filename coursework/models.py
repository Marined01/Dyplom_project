from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None):
        if not email:
            raise ValueError("Користувач повинен мати email")
        user = self.model(email=self.normalize_email(email), name=name, surname=surname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None):
        user = self.create_user(email, name, surname, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def __str__(self):
        return f'{self.surname} {self.name}'


class Key(models.Model):
    STATUS_CHOICES = [
        ('free', 'Вільна'),
        ('taken', 'Зайнята'),
        ('pending', 'Очікує')
    ]

    auditory = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')
    take_key_time = models.DateTimeField(null=True, blank=True)
    put_key_time = models.DateTimeField(null=True, blank=True)
    holder = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Аудиторія {self.auditory} — {self.get_status_display()}"

    def take_key(self, user):
        if self.status == 'taken':
            raise ValueError("Ключ вже зайнятий")

        taken_keys_count = Key.objects.filter(holder=user, status='taken').count()
        if taken_keys_count >= 4:
            raise ValueError("Ви не можете взяти більше 4 ключів одночасно")

        self.status = 'taken'
        self.holder = user
        self.take_key_time = timezone.now()
        self.put_key_time = None
        self.save()

    def put_key(self):
        if self.status == 'free':
            raise ValueError('Ключ не був на руках (аудиторія вільна)')
        self.status = 'free'
        self.holder = None
        self.put_key_time = timezone.now()
        self.save()

    def transfer_key(self, new_user):
        if self.status == 'free':
            raise ValueError('Аудиторія вільна, неможливо передати ключ')
        self.holder = new_user
        self.take_key_time = timezone.now()
        self.save()


class Key_requests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    def is_valid(self):
        return (
                timezone.now() < self.created_at + timedelta(minutes=15)
                and not self.is_expired
                and not self.is_approved)

    def __str__(self):
        return f"Запит від {self.user} на ключ {self.key} — {'Підтверджено' if self.is_approved else 'Очікує'}"

class Key_return_request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    def is_valid(self):
        return (
                timezone.now() < self.created_at + timedelta(minutes=15)
                and not self.is_expired
                and not self.is_approved)

    def __str__(self):
        return f"Запит на повернення ключа {self.key} від {self.user} — {'Підтверджено' if self.is_approved else 'Очікує'}"


class Key_transfer(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers')
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    def is_valid(self):
        return (
                timezone.now() < self.created_at + timedelta(minutes=15)
                and not self.is_expired
                and not self.is_approved)
    def __str__(self):
        return f"Запит на передавання ключа {self.key} від {self.user} — {'Підтверджено' if self.is_approved else 'Очікує'}"