#!/usr/bin/env python

import importlib.util
import os
import sys

sys.path.append(os.path.dirname(__file__))

from config import config

def main():
    for backup_spec in config.get('BACKUP_SPECS', {}).values():
        try:
            execute_backup_spec(backup_spec=backup_spec)
        except Exception as error:
            wrapped_error = (
                "Unable to make backups for spec '{backup_spec}'\n"
                "Error:\n"
                "\t{error}\n"
                "Skipping spec."
            ).format(
                backup_spec=backup_spec,
                error=error
            )
            print(wrapped_error, file=sys.stderr)

def execute_backup_spec(backup_spec=None):
    module = importlib.import_module(backup_spec['module'])
    module.execute_backup_spec(backup_spec=backup_spec)

if __name__ == '__main__':
    main()
