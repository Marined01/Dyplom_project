"""Створити адміністратора з ADMIN_* у середовищі (для Docker)."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Створити staff-користувача з ADMIN_EMAIL і ADMIN_PASSWORD, "
    )

    def handle(self, *args, **options):
        email = os.environ.get("ADMIN_EMAIL", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "").strip()

        if not email or not password:
            self.stdout.write(
                "ADMIN_EMAIL / ADMIN_PASSWORD не задані — пропуск створення адміна."
            )
            return

        name = os.environ.get("ADMIN_NAME", "Admin").strip() or "Admin"
        surname = os.environ.get("ADMIN_SURNAME", "User").strip() or "User"

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Користувач {email} уже існує — нічого не змінюємо.")
            return

        User.objects.create_superuser(
            email=email,
            name=name,
            surname=surname,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Створено адміністратора: {email}"))
