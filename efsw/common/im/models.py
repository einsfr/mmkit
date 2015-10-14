import uuid

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


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
        db_index=True,
        verbose_name='отправитель'
    )

    receiver = models.ForeignKey(
        User,
        related_name='+',
        editable=False,
        db_index=True,
        verbose_name='получатель'
    )

    sended = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='время отправления'
    )

    readed = models.DateTimeField(
        editable=False,
        null=True,
        verbose_name='время прочтения'
    )

    important = models.BooleanField(
        default=False,
        verbose_name='важное'
    )

    msg_class = models.CharField(
        blank=True,
        max_length=64,
        editable=False,
        verbose_name='класс сообщения'
    )


class Conversation(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'разговор'
        verbose_name_plural = 'разговоры'

    TYPE_DIALOG = 0

    TYPES = {
        TYPE_DIALOG: 'диалог'
    }

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    updated = models.DateTimeField(
        editable=False,
        verbose_name='последнее обновление'
    )

    participants = ArrayField(
        models.PositiveIntegerField(),
        verbose_name='участники разговора'
    )

    conv_type = models.IntegerField(
        editable=False,
        choices=TYPES.items(),
        verbose_name='тип разговора'
    )

    def save(self, *args, **kwargs):
        p = self.participants
        if type(self.participants) == 'list':
            self.participants = [u.id for u in self.participants if isinstance(u, User)]
        super().save(*args, **kwargs)
        self.participants = p
