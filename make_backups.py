#!/usr/bin/env python

import importlib.util
import os
import logging
import sys

sys.path.append(os.path.dirname(__file__))

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

from config import config

def main():
    logger.info("Starting backups.")
    for backup_spec in config.get('BACKUP_SPECS', {}).values():
        try:
            label = backup_spec.get('label', '<unlabeled>')
            logger.info("running spec with label '{label}'".format(label=label))
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
    logger.info("Ending backups.")

def execute_backup_spec(backup_spec=None):
    module = importlib.import_module(backup_spec['module'])
    module.execute_backup_spec(backup_spec=backup_spec)

if __name__ == '__main__':
    main()
