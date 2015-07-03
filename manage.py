#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmkit.conf.settings")
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.environ.setdefault("APP_ENV", "test")
    else:
        os.environ.setdefault("APP_ENV", "dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
