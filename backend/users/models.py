from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class StaffUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class StaffUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    objects = StaffUserManager()

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="ID в Telegram"
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Username в Telegram"
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Имя в Telegram"
    )
    last_active = models.DateTimeField(
        default=timezone.now,
        verbose_name="Последняя активность"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

    def __str__(self):
        if self.username:
            return f"@{self.username} ({self.telegram_id})"
        elif self.first_name:
            return f"{self.first_name} ({self.telegram_id})"
        else:
            return str(self.telegram_id)

    def is_inactive(self, days=10):
        """Проверяет, неактивен ли пользователь более N дней"""
        return (timezone.now() - self.last_active).days >= days