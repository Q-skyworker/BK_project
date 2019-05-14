# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver

from gcloud.core.models import Business


@receiver(post_save, sender=Business)
def business_post_save_handler(sender, instance, created, **kwargs):
    if created:
        pass
