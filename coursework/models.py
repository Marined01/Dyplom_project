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
        return f"Авдиторія {self.auditory} — {self.get_status_display()}"

    @property
    def last_activity_at(self):
        # Останній час взяття або повернення
        times = [t for t in (self.take_key_time, self.put_key_time) if t is not None]
        return max(times) if times else None

    @property
    def held_since(self):
        # Коли поточний тримач отримав ключ (лише для статусу «зайнята»)
        if self.status == "taken" and self.take_key_time:
            return self.take_key_time
        return None

    @property
    def held_duration_days(self):
        if not self.held_since:
            return None
        return (timezone.now() - self.held_since).days

    @property
    def held_duration_display(self):
        if not self.held_since:
            return None
        delta = timezone.now() - self.held_since
        days = delta.days
        if days >= 1:
            return f"{days} дн."
        hours = delta.seconds // 3600
        if hours >= 1:
            return f"{hours} год."
        return "менше години"

    def is_long_held(self, threshold_days=None):
        days = self.held_duration_days
        if days is None:
            return False
        if threshold_days is None:
            from coursework.key_metrics import LONG_HELD_DAYS

            threshold_days = LONG_HELD_DAYS
        return days >= threshold_days

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
            raise ValueError('Ключ не був на руках (авдиторія вільна)')
        self.status = 'free'
        self.holder = None
        self.put_key_time = timezone.now()
        self.save()

    def transfer_key(self, new_user):
        if self.status == 'free':
            raise ValueError('Авдиторія вільна, неможливо передати ключ')
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
        return (
            f"Запит на передавання ключа {self.key} від {self.from_user} "
            f"до {self.to_user} — {'Підтверджено' if self.is_approved else 'Очікує'}"
        )