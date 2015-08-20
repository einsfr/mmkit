from efsw.conversion import models
from efsw.conversion.converter import args


def load_data():
    models.ConversionProfile.objects.all().delete()

    cp = models.ConversionProfile()
    cp.id = 1
    cp.name = 'Первый профиль'
    cp.description = 'Простой профиль с одним входом и одним выходом'
    cp.args_builder = args.ArgumentsBuilder([args.Input(comment='Входной файл')], [args.Output()])
    cp.save()

    cp = models.ConversionProfile()
    cp.id = 2
    cp.name = 'Профиль с двумя входами'
    cp.description = 'Профиль с двумя входами и одним выходом'
    cp.args_builder = args.ArgumentsBuilder(
        [
            args.Input(comment='Первый вход (видео)', allowed_ext=['mpv']),
            args.Input(comment='Второй вход (аудио)', allowed_ext=['mpa', 'wav']),
        ],
        [
            args.Output(allowed_ext=['mpg'])
        ]
    )
    cp.save()
