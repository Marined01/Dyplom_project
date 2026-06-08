"""Додати аудиторії з SEED_AUDITORIES у середовищі (для Docker)."""

import os

from django.core.management.base import BaseCommand

from coursework.models import Key


class Command(BaseCommand):
    help = (
        "Створити ключі для номерів з SEED_AUDITORIES (через кому), "
        "якщо такої аудиторії ще немає."
    )

    def handle(self, *args, **options):
        raw = os.environ.get("SEED_AUDITORIES", "").strip()
        if not raw:
            self.stdout.write("SEED_AUDITORIES не задано — пропуск.")
            return

        auditories = [part.strip() for part in raw.split(",") if part.strip()]
        if not auditories:
            self.stdout.write("SEED_AUDITORIES порожнє — пропуск.")
            return

        created = 0
        for auditory in auditories:
            if Key.objects.filter(auditory=auditory).exists():
                continue
            Key.objects.create(auditory=auditory)
            created += 1

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Додано аудиторій: {created} ({', '.join(auditories)})")
            )
        else:
            self.stdout.write("Усі аудиторії з SEED_AUDITORIES уже є в БД.")
