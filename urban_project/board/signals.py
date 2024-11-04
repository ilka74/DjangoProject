"""
В этом файле определены сигналы Django для обновления статистики пользователей на основе действий с объявлениями.
"""
from Tools.demo.mcast import sender
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Advertisement, UserProfile


@receiver(post_save, sender=Advertisement)
# Обновление статистики пользователя при создании объявления
def update_user_statistics_on_create(sender, instance, created, **kwargs):
    if created:
        profile, _ = UserProfile.objects.get_or_create(user=instance.author)
        profile.advertisements_count += 1
        profile.save()


@receiver(post_delete, sender=Advertisement)
# Обновление статистики пользователя при удалении объявления
def update_user_statistics_on_delete(sender, instance, **kwargs):
    profile = UserProfile.objects.get(user=instance.author)
    profile.advertisements_count -= 1
    profile.save()


@receiver(post_save, sender=Advertisement)
# Обновление статистики пользователя при лайках
def update_user_statistics_on_like(sender, instance, **kwargs):
    if instance.likes > 0:
        profile = UserProfile.objects.get(user=instance.author)
        profile.total_likes += 1
        profile.save()


@receiver(post_save, sender=Advertisement)
# Обновление статистики пользователя при дизлайках
def update_user_statistics_on_dislike(sender, instance, **kwargs):
    if instance.dislikes > 0:
        profile = UserProfile.objects.get(user=instance.author)
        profile.total_dislikes += 1
        profile.save()
