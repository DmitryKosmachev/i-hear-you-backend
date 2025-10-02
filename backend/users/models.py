from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class StaffUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Please enter email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class StaffUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField()
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    objects = StaffUserManager()

    class Meta:
        verbose_name = 'Staff user'
        verbose_name_plural = 'Staff users'


class BotUser(models.Model):
    telegram_id = models.BigIntegerField('Telegram ID', unique=True)
    username = models.CharField('Username', blank=True, null=True)
    first_name = models.CharField('First name', blank=True, null=True)
    last_active = models.DateTimeField('Last active', default=timezone.now)
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Sign-up date', auto_now_add=True)

    class Meta:
        verbose_name = 'bot user'
        verbose_name_plural = 'Bot users'

    def __str__(self):
        if self.username:
            return f'@{self.username} ({self.telegram_id})'
        elif self.first_name:
            return f'{self.first_name} ({self.telegram_id})'
        else:
            return str(self.telegram_id)

    def is_inactive(self, days=10):
        """Check if the user was inactive for more than N days."""
        return (timezone.now() - self.last_active).days >= days


class StatBotUser(models.Model):
    telegram_id = models.BigIntegerField('Telegram ID', unique=True)
    username = models.CharField('Username', blank=True, null=True)
    first_name = models.CharField('First name', blank=True, null=True)
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Sign-up date', auto_now_add=True)

    class Meta:
        verbose_name = 'stat bot user'
        verbose_name_plural = 'Stat bot users'

    def __str__(self):
        if self.username:
            return f'@{self.username} ({self.telegram_id})'
        elif self.first_name:
            return f'{self.first_name} ({self.telegram_id})'
        else:
            return str(self.telegram_id)
