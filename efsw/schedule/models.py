from django.db import models
from django.core import urlresolvers
from django.core.exceptions import ValidationError


class Channel(models.Model):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'канал'
        verbose_name_plural = 'каналы'

    name = models.CharField(
        max_length=64,
        verbose_name='название',
        unique=True
    )

    active = models.BooleanField(
        verbose_name='используется',
        default=True
    )


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
        verbose_name='используется с'
    )

    active_until = models.DateField(
        verbose_name='используется до',
        null=True
    )

    active = models.BooleanField(
        verbose_name='используется',
        default=False
    )

    start_time = models.TimeField(
        verbose_name='время начала эфирных суток'
    )

    end_time = models.TimeField(
        verbose_name='время окончания эфирных суток'
    )

    channel = models.ForeignKey(
        Channel,
        related_name='lineups'
    )

    def __str__(self):
        return self.name


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
        verbose_name='ограничение по возрасту'
    )

    color = models.CharField(
        verbose_name='цвет фона',
        max_length=7,
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

    def clean(self):
        lineup = self.lineup
        if lineup.start_time < lineup.end_time:
            if self.start_time == self.end_time:
                raise ValidationError(
                    'Время начала и окончания фрагмента может совпадать только в круглосуточной сетке'
                )

        elif lineup.end_time < lineup.start_time:
            if self.start_time == self.end_time:
                raise ValidationError(
                    'Время начала и окончания фрагмента может совпадать только в круглосуточной сетке'
                )
            if lineup.end_time <= self.start_time < lineup.start_time:
                raise ValidationError(
                    'Время начала фрагмента находится вне временных границ сетки'
                )
            if lineup.end_time < self.end_time <= lineup.start_time:
                raise ValidationError(
                    'Время окончания фрагмента находится вне временных границ сетки'
                )
            if (self.start_time > self.end_time) and self.end_time > lineup.start_time:
                raise ValidationError(
                    'Окончание фрагмента находится раньше его начала'
                )
        else:
            # т.е. если сетка круглосуточная
            if self.start_time < lineup.start_time < self.end_time:
                raise ValidationError(
                    'В круглосуточной сетке фрагмент не может начинаться в одни эфирные сутки, а заканчиваться в другие'
                )