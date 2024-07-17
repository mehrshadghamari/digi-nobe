# Generated by Django 4.2 on 2024-07-17 14:17

import apps.account.models
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 30 characters or fewer starting with a letter. Letters, digits and underscore only.",
                        max_length=32,
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[a-zA-Z][a-zA-Z0-9_\\.]+$",
                                "Enter a valid username starting with a-z. This value may contain only letters, numbers and underscore characters.",
                                "invalid",
                            )
                        ],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                (
                    "national_code",
                    models.CharField(blank=True, max_length=10, null=True, unique=True),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "phone_number",
                    models.BigIntegerField(
                        error_messages={
                            "unique": "A user with this mobile number already exists."
                        },
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^989[0-3,9]\\d{8}$",
                                "Enter a valid mobile number.",
                                "invalid",
                            )
                        ],
                        verbose_name="mobile number",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "last_seen",
                    models.DateTimeField(null=True, verbose_name="last seen date"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "db_table": "users",
            },
            managers=[
                ("objects", apps.account.models.UserManager()),
            ],
        ),
    ]
