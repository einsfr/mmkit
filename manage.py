#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmkit.conf.test")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmkit.conf.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
