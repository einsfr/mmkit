from django.db import models


class ConversionProcess(models.Model):

    conv_id = models.UUIDField(
        unique=True,
        editable=False
    )

    pid = models.PositiveIntegerField(
        editable=False
    )
