import uuid

from django.db import models


class MessageParticipant(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'участник обмена сообщениями'
        verbose_name_plural = 'участники обмена сообщениями'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4
    )


class Message(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4
    )

    content = models.TextField(
        verbose_name='содержание',
    )

    sender = models.ForeignKey(
        MessageParticipant,
        related_name='sended_messages',
        editable=False,
        verbose_name='отправитель'
    )

    reciever = models.ForeignKey(
        MessageParticipant,
        related_name='recieved_messages',
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
