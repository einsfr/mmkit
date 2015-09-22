from efsw.conversion import models
from efsw.conversion.converter import args


def load_data():
    models.ConversionTask.objects.all().delete()

    ct = models.ConversionTask()
    ct.id = 'e0593092-fbc5-4b20-99f4-677f8954220f'
    ct.name = 'Тестовое задание 1'
    ct.io_conf = args.IOPathConfiguration(['test.in'], ['test.out'])
    ct.conv_profile_id = 1
    ct.save()
