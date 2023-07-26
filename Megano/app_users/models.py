from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from photologue.models import Photo


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', null=True, default=None, on_delete=models.CASCADE)
    patronymic = models.CharField(verbose_name='Отчество', max_length=120, blank=True)
    phone = models.IntegerField(verbose_name="Телефон", null=True, default=None)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    avatar = models.ForeignKey(
        Photo,
        verbose_name="Аватар",
        on_delete=models.SET_NULL,
        null=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("account", kwargs={"user_slug": self.slug})

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """Create Profile after registration"""
        if created:
            UserProfile.objects.create(user=instance,slug=instance)
