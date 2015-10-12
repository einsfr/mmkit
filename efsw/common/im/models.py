import uuid

from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    content = models.TextField(
        verbose_name='содержание',
    )

    sender = models.ForeignKey(
        User,
        null=True,
        related_name='+',
        editable=False,
        verbose_name='отправитель'
    )

    receiver = models.ForeignKey(
        User,
        related_name='+',
        editable=False,
        verbose_name='получатель'
    )

    sended = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='время отправления'
    )

    readed = models.DateTimeField(
        editable=False,
        verbose_name='время прочтения'
    )

    important = models.BooleanField(
        default=False,
        verbose_name='важное'
    )

    postponed = models.BooleanField(
        default=False,
        verbose_name='отложено'
    )

    msg_class = models.CharField(
        blank=True,
        max_length=64,
        editable=False,
        verbose_name='класс сообщения'
    )
