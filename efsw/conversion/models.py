import uuid
import pickle
import os.path

from django.db import models
from django.core.exceptions import ValidationError

from efsw.common.db.models.ordered_model import OrderedModel
from efsw.conversion.converter import args
from efsw.conversion.converter.exceptions import IOPathResolveException
from efsw.conversion import errors


class ConversionProcess(models.Model):

    class Meta:
        verbose_name = 'процесс конвертирования'
        verbose_name_plural = 'процессы конвертирования'
        app_label = 'conversion'

    conv_id = models.UUIDField(
        unique=True,
        editable=False
    )

    pid = models.PositiveIntegerField(
        editable=False
    )


class ConversionProfile(models.Model):

    class Meta:
        verbose_name = 'профиль конвертирования'
        verbose_name_plural = 'профили конвертирования'
        app_label = 'conversion'
        ordering = ['-id']

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

    class Meta:
        verbose_name = 'задание конвертирования'
        verbose_name_plural = 'задания конвертирования'
        app_label = 'conversion'
        ordering = ['-added']

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
            raise ValidationError(errors.CONVERSION_TASK_NO_AB_NO_CP)
        if self.args_builder is not None and self.conv_profile is not None:
            raise ValidationError(errors.CONVERSION_TASK_BOTH_AB_AND_CP)
        if self.args_builder is not None and not isinstance(self.args_builder, args.ArgumentsBuilder):
            raise ValidationError(errors.CONVERSION_TASK_AB_WRONG_CLASS)
        if not isinstance(self.io_conf, args.IOPathConfiguration):
            raise ValidationError(errors.CONVERSION_TASK_IO_CONF_WRONG_CLASS)
        # Проверка соответствия количества входов-выходов профиля (или args_builder'а) конфигурации входов-выходов
        args_builder = self.args_builder if self.args_builder is not None else self.conv_profile.args_builder
        ab_inputs = args_builder.inputs
        if len(ab_inputs) != len(self.io_conf.input_paths):
            raise ValidationError(
                errors.CONVERSION_TASK_IN_COUNT_MISMATCH.format(len(ab_inputs), len(self.io_conf.input_paths))
            )
        ab_outputs = args_builder.outputs
        if len(ab_outputs) != len(self.io_conf.output_paths):
            raise ValidationError(
                errors.CONVERSION_TASK_OUT_COUNT_MISMATCH.format(len(ab_outputs), len(self.io_conf.output_paths))
            )
        # Проверка на соответствие заданных путей разрешённым расширениям
        try:
            in_paths, out_paths = self.io_conf.build()
        except IOPathResolveException as e:
            raise ValidationError(str(e))
        io_paths = in_paths + out_paths
        for k, io in enumerate(ab_inputs + ab_outputs):
            if io.allowed_ext:
                ext = os.path.splitext(io_paths[k])[1]
                if not ext:
                    raise ValidationError(
                        errors.CONVERSION_TASK_FILE_EXT_REQUIRED.format(os.path.split(io_paths[k])[1])
                    )
                if ext[1:] not in io.allowed_ext:
                    raise ValidationError(
                        errors.CONVERSION_TASK_FILE_EXT_INVALID.format(
                            os.path.split(io_paths[k])[1], ', '.join(io.allowed_ext)
                        )
                    )
