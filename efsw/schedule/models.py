import datetime
import uuid

from django.db import models
from django.core import urlresolvers
from django.core.exceptions import ValidationError

from efsw.common.db.models.fields.color import ColorField
from efsw.common.db.models.ordered_model import OrderedModel
import efsw.archive.models as archive_models


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

    ERR_TEXT_START_END_EQUAL = 'Время начала и окончания фрагмента может совпадать только в круглосуточной сетке.'
    ERR_TEXT_START_END_EQUAL_24 = 'Время начала и окончания фрагмента в круглосуточной сетке может совпадать только ' \
                                  'если они равны времени начала (и окончания) сетки.'
    ERR_TEXT_END_BEFORE_START = 'Окончание фрагмента находится раньше его начала.'
    ERR_TEXT_START_OUT_OF_RANGE = 'Время начала фрагмента находится вне временных границ сетки.'
    ERR_TEXT_END_OUT_OF_RANGE = 'Время окончания фрагмента находится вне временных границ сетки.'
    ERR_TEXT_DAY_MISMATCH = 'В круглосуточной сетке фрагмент не может начинаться в одни эфирные сутки, ' \
                            'а заканчиваться в другие.'

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
            if self.end_time < self.start_time < lineup.start_time:
                raise ValidationError(self.ERR_TEXT_END_BEFORE_START)
            if lineup.start_time < self.end_time < self.start_time:
                raise ValidationError(self.ERR_TEXT_END_BEFORE_START)
            if self.start_time == self.end_time and (self.start_time != lineup.start_time):
                raise ValidationError(self.ERR_TEXT_START_END_EQUAL_24)


class AbstractDayLineup(models.Model):

    class Meta:
        app_label = 'schedule'
        abstract = True

    start_time = models.TimeField(
        verbose_name='время начала эфирных суток'
    )

    end_time = models.TimeField(
        verbose_name='время окончания эфирных суток'
    )

    channel = models.ForeignKey(
        Channel,
        related_name='+',
        verbose_name='канал',
    )


class DayLineup(AbstractDayLineup):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'программа на день'
        verbose_name_plural = 'программы на день'

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    day = models.DateField(
        verbose_name='дата'
    )


class AbstractDayLineupItem(OrderedModel):

    class Meta:
        app_label = 'schedule'
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )


class DayLineupItem(AbstractDayLineupItem):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'элемент программы на день'
        verbose_name_plural = 'элементы программы на день'

    day_lineup = models.ForeignKey(
        DayLineup,
        related_name='items',
        verbose_name='программа на день'
    )


class DayLineupTemplate(AbstractDayLineup):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'шаблон программы на день'
        verbose_name_plural = 'шаблоны программ на день'

    name = models.CharField(
        verbose_name='имя шаблона',
        unique=True,
        max_length=255
    )


class DayLineupTemplateItem(AbstractDayLineupItem):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'элемент шаблона программы на день'
        verbose_name_plural = 'элементы шаблона программы на день'

    day_lineup_template = models.ForeignKey(
        DayLineupTemplate,
        related_name='items',
        verbose_name='шаблон программы на день'
    )


class ProgramSeries(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'цикл программ'
        verbose_name_plural = 'циклы программ'
        unique_together = ('program', 'name')

    name = models.CharField(
        verbose_name='название цикла',
        max_length=255
    )

    program = models.ForeignKey(
        Program,
        related_name='series',
        verbose_name='программа'
    )


class ProgramIssue(OrderedModel):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'выпуск программы'
        verbose_name_plural = 'выпуски программы'
        unique_together = ('series', 'code')

    order_domain_field = 'series'

    name = models.CharField(
        verbose_name='название',
        max_length=255,
        unique=True
    )

    series = models.ManyToManyField(
        ProgramSeries,
        related_name='issues',
        verbose_name='цикл программ'
    )

    code = models.CharField(
        verbose_name='код',
        max_length=32
    )

    archive_item = models.ForeignKey(
        archive_models.Item,
        related_name='+',
        verbose_name='элемент архива',
        null=True
    )


class ProgramIssuePart(OrderedModel):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'часть выпуска программы'
        verbose_name_plural = 'части выпуска программы'

    order_domain_field = 'issue'

    issue = models.ForeignKey(
        ProgramIssue,
        related_name='parts',
        verbose_name='выпуск программы'
    )

    file_path = models.CharField(
        verbose_name='путь к файлу (или его имя)',
        max_length=255,
    )

    duration = models.TimeField(
        verbose_name='длительность',
    )
