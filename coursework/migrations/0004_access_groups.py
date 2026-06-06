# Generated manually for access groups feature
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coursework", "0003_key_transfer"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        verbose_name="Назва групи",
                    ),
                ),
            ],
            options={
                "verbose_name": "Група доступу",
                "verbose_name_plural": "Групи доступу",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="user",
            name="access_groups",
            field=models.ManyToManyField(
                blank=True,
                related_name="members",
                to="coursework.accessgroup",
                verbose_name="Групи доступу",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="allowed_keys",
            field=models.ManyToManyField(
                blank=True,
                related_name="users_with_personal_access",
                to="coursework.key",
                verbose_name="Додаткові аудиторії",
            ),
        ),
        migrations.AddField(
            model_name="accessgroup",
            name="keys",
            field=models.ManyToManyField(
                blank=True,
                related_name="access_groups",
                to="coursework.key",
                verbose_name="Дозволені аудиторії",
            ),
        ),
    ]
