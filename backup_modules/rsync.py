import os
import shutil

from . import snapshot_utils

DEFAULT_PARAMS = {
    'BACKUP_ROOT': os.environ.get('HOME', '') + '/backups/rsync',
    'RSYNC_OPTS': '-aR --delete',
}

def execute_backup_spec(backup_spec=None):
    params = {**DEFAULT_PARAMS, **backup_spec.get('params', {})}
    snapshot_utils.default_execute_backup_spec(
        backup_spec=backup_spec,
        snapshot_generator=RsyncSnapshotGenerator(params=params),
        params=params
    )

class RsyncSnapshotGenerator(object):
    def __init__(self, params=None):
        self.params = params

    def generate_snapshot(self, snapshot_dir=None, most_recent_snapshot_dir=None):
        if not most_recent_snapshot_dir:
            os.makedirs(snapshot_dir, exist_ok=True)
        else:
            shutil.copytree(most_recent_snapshot_dir, snapshot_dir)
        for rsync_spec in self.params.get('RSYNC_SPECS', []):
            rsync_opts = rsync_spec.get('rsync_opts', '') or \
                    self.params.get('RSYNC_OPTS', '')
            rsync_cmd = (
                'rsync {rsync_opts} {src} {dest}'
            ).format(
                rsync_opts=rsync_opts,
                src=rsync_spec['src'],
                dest=snapshot_dir,
            )
            snapshot_utils.run_cmd(cmd=rsync_cmd)
