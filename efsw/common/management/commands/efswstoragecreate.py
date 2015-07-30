import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from efsw.common.models import FileStorage
from efsw.common.storage import utils as storage_utils


class Command(BaseCommand):

    help = 'Creates a new storage.'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='Storage\'s name'
        )
        parser.add_argument(
            'base_dir',
            help='Storage\'s base directory name inside EFSW_STORAGE_ROOT '
                 '(relative, without leading or trailing slashes).'
        )
        parser.add_argument(
            '-i', '--id',
            action='store',
            dest='id',
            default=None,
            help='If set, storage will be created with specified id (UUID).'
        )
        parser.add_argument(
            '-w', '--read-write',
            action='store_true',
            dest='read_write',
            default=False,
            help='If set, storage will work in read-write mode, allowing changes.'
        )
        parser.add_argument(
            '-c', '--create-dir',
            action='store_true',
            dest='create_dir',
            default=False,
            help='If set, nonexistent base_dir directory will be created. If not and base_dir directory doesn\'t exist,'
                 ' an exception will be thrown.'
        )
        parser.add_argument(
            '-t', '--test-run',
            action='store_true',
            dest='test_run',
            default=False,
            help='If set, no file system or database operations will be performed. Use this flag for testing purposes.'
        )

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        base_dir_abs = os.path.realpath('{0}/{1}'.format(
            settings.EFSW_STORAGE_ROOT,
            options['base_dir']
        ))
        storage_root = os.path.realpath(settings.EFSW_STORAGE_ROOT)
        if verbosity >= 1:
            print('Base_dir absolute path: {0}'.format(base_dir_abs))
            print('Root absolute path: {0}'.format(storage_root))
            if verbosity > 1:
                print('Check if storage root exists...')
            if options['test_run']:
                print('-t (--test-run) flag was set - THIS IS A TEST RUN, NO CHANGES WILL BE MADE.')
        if not os.path.isdir(storage_root):
            raise CommandError('EFSW_STORAGE_ROOT directory ({0}) doesn\'t exist.'.format(storage_root))
        if verbosity > 1:
            print('Check if base_dir is a subdirectory of storage root...')
        if not storage_utils.is_subdir(storage_root, base_dir_abs):
            raise CommandError(
                'Directory in base_dir argument ({0}) is not a subdirectory of EFSW_STORAGE_ROOT ({1}).'.format(
                    base_dir_abs, storage_root
                )
            )
        if verbosity > 1:
            print('Check if base_dir exists...')
        if not os.path.isdir(base_dir_abs):
            if verbosity >= 1:
                print('Base_dir directory doesn\'t exist.')
            if not options['create_dir']:
                raise CommandError(
                    'Base_dir directory doesn\'t exist. If you want it to be created automatically, '
                    'use -c (--create-dir) flag.'
                )
            else:
                if verbosity >= 1:
                    print('-c (--create-dir) flag was set - creating base_dir directory...')
                if not options['test_run']:
                    os.makedirs(base_dir_abs, settings.EFSW_STORAGE_BASE_DIR_MODE)
        if verbosity > 1:
            print('Check if storage with same base_dir already exists...')
        base_dir = os.path.relpath(base_dir_abs, storage_root)
        if FileStorage.objects.filter(base_dir=base_dir).exists():
            raise CommandError('Storage with base_dir {0} already exists.'.format(base_dir))
        if verbosity > 1:
            print('Creating storage model instance...')
        fs = FileStorage()
        if options['id']:
            fs.id = options['id']
        fs.name = options['name']
        fs.base_dir = base_dir
        fs.read_only = not options['read_write']
        if verbosity > 1:
            print('Validating storage model instance...')
        fs.full_clean()
        if verbosity > 1:
            print('Model instance is valid.')
        if fs.id:
            if verbosity > 1:
                print('ID was set - check if storage with same ID already exists...')
            if FileStorage.objects.filter(id=fs.id).exists():
                raise CommandError('Storage with ID {0} already exists - use efswstoragemod command.'.format(fs.id))
        if not options['test_run']:
            fs.save(force_insert=True)
        if verbosity >= 1:
            print('Storage model instance saved.')
