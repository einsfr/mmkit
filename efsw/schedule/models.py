import datetime

from django.db import models
from django.core import urlresolvers
from django.core.exceptions import ValidationError

from efsw.common.db.models.fields.color import ColorField


class Channel(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'канал'
        verbose_name_plural = 'каналы'
        ordering = ['name']

    name = models.CharField(
        max_length=64,
        verbose_name='название',
        unique=True
    )

    active = models.BooleanField(
        verbose_name='используется',
        default=True
    )

    def __str__(self):
        return self.name


class Lineup(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'сетка вещания'
        verbose_name_plural = 'сетки вещания'

    name = models.CharField(
        max_length=255,
        verbose_name='название',
        unique=True
    )

    active_since = models.DateField(
        verbose_name='используется с',
        null=True
    )

    active_until = models.DateField(
        verbose_name='используется до',
        null=True
    )

    draft = models.BooleanField(
        verbose_name='черновик',
        default=True
    )

    start_time = models.TimeField(
        verbose_name='время начала эфирных суток'
    )

    end_time = models.TimeField(
        verbose_name='время окончания эфирных суток'
    )

    channel = models.ForeignKey(
        Channel,
        related_name='lineups',
        verbose_name='канал'
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse('efsw.schedule:lineup:show', args=(self.id, ))

    def is_editable(self):
        return self.draft

    def is_returnable_to_draft(self):
        return not self.draft and self.active_since > datetime.date.today()


class Program(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'программа'
        verbose_name_plural = 'программы'

    AGE_LIMIT_0 = 0
    AGE_LIMIT_6 = 6
    AGE_LIMIT_12 = 12
    AGE_LIMIT_16 = 16
    AGE_LIMIT_18 = 18

    AGE_LIMIT_DICT = {
        AGE_LIMIT_0: '0+',
        AGE_LIMIT_6: '6+',
        AGE_LIMIT_12: '12+',
        AGE_LIMIT_16: '16+',
        AGE_LIMIT_18: '18+',
    }

    name = models.CharField(
        max_length=255,
        verbose_name='название',
        unique=True
    )

    lineup_size = models.TimeField(
        verbose_name='размер в сетке вещания'
    )

    max_duration = models.TimeField(
        verbose_name='максимальный хронометраж'
    )

    min_duration = models.TimeField(
        verbose_name='минимальный хронометраж'
    )

    description = models.TextField(
        verbose_name='описание'
    )

    age_limit = models.SmallIntegerField(
        choices=AGE_LIMIT_DICT.items(),
        default=AGE_LIMIT_0,
        verbose_name='ограничение по возрасту'
    )

    color = ColorField(
        verbose_name='цвет фона',
        default='#ffffff'
    )

    def get_absolute_url(self):
        return urlresolvers.reverse('efsw.schedule:program:show', args=(self.id, ))

    def format_age_limit(self):
        try:
            return self.AGE_LIMIT_DICT[self.age_limit]
        except KeyError:
            return 'Ошибка: неизвестное значение ограничения по возрасту.'

    def __str__(self):
        return self.name

    ERR_TEXT_LSIZE_SHORTER_THAN_DURATION = 'Размер программы в сетке вещания не может быть меньше её хронометража.'
    ERR_TEXT_MAX_SHORTER_THAN_MIN = 'Максимальный хронометраж программы не может быть меньше минимального.'

    def clean(self):
        if self.lineup_size is None or self.max_duration is None or self.min_duration is None:
            return
        if self.lineup_size < self.max_duration or self.lineup_size < self.min_duration:
            raise ValidationError(self.ERR_TEXT_LSIZE_SHORTER_THAN_DURATION)
        if self.max_duration < self.min_duration:
            raise ValidationError(self.ERR_TEXT_MAX_SHORTER_THAN_MIN)


class ProgramPosition(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'положение программы в сетке вещания'
        verbose_name_plural = 'положения программы в сетке вещания'

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    DOW_DICT = {
        MONDAY: 'Понедельник',
        TUESDAY: 'Вторник',
        WEDNESDAY: 'Среда',
        THURSDAY: 'Четверг',
        FRIDAY: 'Пятница',
        SATURDAY: 'Суббота',
        SUNDAY: 'Воскресенье',
    }

    dow = models.SmallIntegerField(
        verbose_name='день недели',
        choices=DOW_DICT.items()
    )

    start_time = models.TimeField(
        verbose_name='время начала'
    )

    end_time = models.TimeField(
        verbose_name='время окончания'
    )

    comment = models.CharField(
        verbose_name='комментарий',
        max_length=32,
        blank=True
    )

    locked = models.BooleanField(
        verbose_name='заблокировано',
        default=False
    )

    lineup = models.ForeignKey(
        Lineup,
        related_name='program_positions'
    )

    program = models.ForeignKey(
        Program,
        related_name='lineup_positions',
        null=True,
        blank=True,
    )

    ERR_TEXT_START_END_EQUAL = 'Время начала и окончания фрагмента может совпадать только в круглосуточной сетке'
    ERR_TEXT_END_BEFORE_START = 'Окончание фрагмента находится раньше его начала'
    ERR_TEXT_START_OUT_OF_RANGE = 'Время начала фрагмента находится вне временных границ сетки'
    ERR_TEXT_END_OUT_OF_RANGE = 'Время окончания фрагмента находится вне временных границ сетки'
    ERR_TEXT_DAY_MISMATCH = 'В круглосуточной сетке фрагмент не может начинаться в одни эфирные сутки, ' \
                            'а заканчиваться в другие'

    def clean(self):
        lineup = self.lineup
        if lineup.start_time < lineup.end_time:
            if self.start_time == self.end_time:
                raise ValidationError(self.ERR_TEXT_START_END_EQUAL)
            if self.start_time > self.end_time:
                raise ValidationError(self.ERR_TEXT_END_BEFORE_START)
            if self.start_time < lineup.start_time or self.start_time >= lineup.end_time:
                raise ValidationError(self.ERR_TEXT_START_OUT_OF_RANGE)
            if self.end_time <= lineup.start_time or self.end_time > lineup.end_time:
                raise ValidationError(self.ERR_TEXT_END_OUT_OF_RANGE)
        elif lineup.end_time < lineup.start_time:
            if self.start_time == self.end_time:
                raise ValidationError(self.ERR_TEXT_START_END_EQUAL)
            if lineup.end_time <= self.start_time < lineup.start_time:
                raise ValidationError(self.ERR_TEXT_START_OUT_OF_RANGE)
            if lineup.end_time < self.end_time <= lineup.start_time:
                raise ValidationError(self.ERR_TEXT_END_OUT_OF_RANGE)
            if (self.start_time > self.end_time) and self.end_time > lineup.start_time:
                raise ValidationError(self.ERR_TEXT_END_BEFORE_START)
        else:
            # т.е. если сетка круглосуточная
            if self.start_time < lineup.start_time < self.end_time:
                raise ValidationError(self.ERR_TEXT_DAY_MISMATCH)