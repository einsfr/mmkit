import uuid
import pickle

from django.db import models
from django.core.exceptions import ValidationError

from efsw.common.db.models.ordered_model import OrderedModel
from efsw.conversion.converter import args


class ConversionProcess(models.Model):

    conv_id = models.UUIDField(
        unique=True,
        editable=False
    )

    pid = models.PositiveIntegerField(
        editable=False
    )


class ConversionProfile(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(
        verbose_name='название',
        unique=True,
        max_length=255
    )

    description = models.TextField(
        verbose_name='описание',
        blank=True
    )

    args_builder = models.BinaryField(
        editable=False
    )

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance.args_builder = pickle.loads(instance.args_builder)
        return instance

    def save(self, *args, **kwargs):
        args_builder = self.args_builder
        self.args_builder = pickle.dumps(self.args_builder)
        super().save(*args, **kwargs)
        self.args_builder = args_builder


class ConversionTask(OrderedModel):

    STATUS_UNKNOWN = 0

    STATUS_ENQUEUED = 1
    STATUS_START_WAITING = 2
    STATUS_STARTED = 3
    STATUS_IN_PROGRESS = 4
    STATUS_COMPLETED = 5
    STATUS_CANCELED = 6

    STATUS_ERROR = -1

    STATUSES = {
        STATUS_UNKNOWN: 'неизвестно',

        STATUS_ENQUEUED: 'в очереди',
        STATUS_START_WAITING: 'ожидает запуска',
        STATUS_STARTED: 'запущено',
        STATUS_IN_PROGRESS: 'выполняется',
        STATUS_COMPLETED: 'завершено',
        STATUS_CANCELED: 'отменено',

        STATUS_ERROR: 'ошибка'
    }

    ERROR_MAX_LENGTH = 1024

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    args_builder = models.BinaryField(
        null=True,
        editable=False
    )

    io_conf = models.BinaryField(
        editable=False
    )

    status = models.IntegerField(
        editable=False,
        choices=STATUSES.items(),
        default=STATUS_ENQUEUED
    )

    added = models.DateTimeField(
        editable=False,
        auto_now_add=True
    )

    updated = models.DateTimeField(
        editable=False,
        auto_now=True
    )

    processed_frames = models.PositiveIntegerField(
        editable=False,
        null=True
    )

    error_msg = models.CharField(
        blank=True,
        editable=False,
        max_length=ERROR_MAX_LENGTH
    )

    conv_profile = models.ForeignKey(
        ConversionProfile,
        null=True,
        related_name='+',
        editable=False
    )

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        if instance.args_builder:
            instance.args_builder = pickle.loads(instance.args_builder)
        if instance.io_conf:
            instance.io_conf = pickle.loads(instance.io_conf)
        return instance

    def save(self, *args, **kwargs):
        args_builder = self.args_builder
        io_conf = self.io_conf
        if self.args_builder:
            self.args_builder = pickle.dumps(self.args_builder)
        if self.io_conf:
            self.io_conf = pickle.dumps(self.io_conf)
        super().save(*args, **kwargs)
        self.args_builder = args_builder
        self.io_conf = io_conf

    def clean(self):
        if self.args_builder is None and self.conv_profile is None:
            raise ValidationError('Не заданы настройки конвертирования. Необходимо установить поля self.args_builder '
                                  'или self.conv_profile.')
        if self.args_builder is not None and self.conv_profile is not None:
            raise ValidationError('Модель не может одновременно иметь установленные поля self.args_builder '
                                  'и self.conv_profile.')
        if self.args_builder is not None and not isinstance(self.args_builder, args.ArgumentsBuilder):
            raise ValidationError('Поле модели args_builder должно содержать экземпляр класса ArgumentsBuilder '
                                  'или его потомка.')
        if not isinstance(self.io_conf, args.IOPathConfiguration):
            raise ValidationError('Поле модели io_conf должно содержать экземпляр класса IOPathConfiguration '
                                  'или его потомка.')
        # Проверка соответствия количества входов-выходов профиля (или args_builder'а) конфигурации входов-выходов
        args_builder = self.args_builder if self.args_builder is not None else self.conv_profile.args_builder
        if len(args_builder.inputs) != len(self.io_conf.input_paths):
            raise ValidationError('Количество входов не совпадает с количеством заданных путей.')
        if len(args_builder.outputs) != len(self.io_conf.output_paths):
            raise ValidationError('Количество выходов не совпадает с количеством заданных путей.')
        # Проверка соответствия файлов в путях разрешённым расширениям
        # Проверка хранилищ на предмет разрешённых действий с ними
        pass
