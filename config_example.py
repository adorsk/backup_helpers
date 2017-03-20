import os


config = {}
config['BACKUP_ROOT'] = os.environ.get('HOME', '') + '/backups'
config['JUNK_DIR'] = os.path.join(config['BACKUP_ROOT'], 'junk')
os.makedirs(config['JUNK_DIR'], exist_ok=True)

config['DEFAULT_PARAMS'] = {
    'JUNK_DIR': config['JUNK_DIR'],
    'DAILY_BACKUPS': {
        'DAYS_TO_KEEP': 7,
    },
    'MONTHLY_BACKUPS': {
        'MONTHS_TO_KEEP': 3,
        'DAY_OF_MONTH': 20,
    }
}

config['BACKUP_SPECS'] = {
    'postgres': {
        'module': 'backup_modules.postgres',
        'params': {
            **config['DEFAULT_PARAMS'],
            'BACKUP_ROOT': os.path.join(config['BACKUP_ROOT'], 'postgres'),
            'DB_USER': 'postgres',
        }
    },
    'rsync': {
        'module': 'backup_modules.rsync',
        'params': {
            **config['DEFAULT_PARAMS'],
            'BACKUP_ROOT': os.path.join(config['BACKUP_ROOT'], 'rsync'),
            'RSYNC_SPECS': []
        }
    },
}
