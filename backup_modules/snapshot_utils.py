import datetime
import glob
import os
import re
import shutil
import subprocess


SNAPSHOT_TAG = 'snapshot'
TIME_FMT = '%Y%m%d_%H%M%S'

def get_snapshot_time(snapshot_name):
    snapshot_re = '{snapshot_tag}\.(.+)'.format(snapshot_tag=SNAPSHOT_TAG)
    m = re.search(snapshot_re, snapshot_name)
    if m:
        timestr = m.group(1)
        return datetime.datetime.strptime(timestr, TIME_FMT)

def get_most_recent_snapshot(snapshots_dir=None):
    snapshots = list_snapshots(snapshots_dir=snapshots_dir)
    if not snapshots: return None
    return sorted(snapshots, key=get_snapshot_time)[-1]

def list_snapshots(snapshots_dir=None):
    snapshots = glob.glob(snapshots_dir + '/*' + SNAPSHOT_TAG + '.*')
    return snapshots

def generate_snapshot_suffix(time=None):
    if not time: time = datetime.datetime.now()
    return '{snapshot_tag}.{time_tag}'.format(
        snapshot_tag=SNAPSHOT_TAG,
        time_tag=datetime.datetime.strftime(time, TIME_FMT)
    )

def purge_expired_snapshots(snapshots_dir=None, expiration_time=None,
                            junk_dir=None):
    snapshots = list_snapshots(snapshots_dir=snapshots_dir)
    for snapshot in snapshots:
        snapshot_time = get_snapshot_time(snapshot_name=snapshot)
        if snapshot_time <= expiration_time:
            if not junk_dir: shutil.rmtree(snapshot)
            else: shutil.move(snapshot, junk_dir)

def run_cmd(cmd=None, run_kwargs=None):
    default_run_kwargs = {'shell': True, 'check': True,
                          'stdout': subprocess.PIPE}
    run_kwargs =  {**default_run_kwargs, **(run_kwargs or {})}
    try:
        return subprocess.run(cmd, **run_kwargs)
    except Exception as error:
        wrapped_error = (
            "Error running command. Command was:\n"
            "\t{cmd}\n"
            "Error was:\n"
            "\t{error}"
        ).format(
            cmd=cmd,
            error=error
        )
        raise Exception(wrapped_error)


def default_execute_backup_spec(backup_spec=None, snapshot_generator=None,
                                params=None):
    daily_snaps_dir = os.path.join(params['BACKUP_ROOT'], 'daily_snapshots')
    snap_basename = generate_snapshot_suffix()
    daily_snap = os.path.join(daily_snaps_dir, snap_basename)
    most_recent_snap = get_most_recent_snapshot(snapshots_dir=daily_snaps_dir)
    snapshot_generator.generate_snapshot(
        snapshot_dir=daily_snap,
        most_recent_snapshot_dir=most_recent_snap
    )
    now = datetime.datetime.now()
    days_to_keep = params.get('DAILY_BACKUPS', {}).get('DAYS_TO_KEEP', 7)
    daily_snaps_expiration_time = now - datetime.timedelta(days=days_to_keep)
    purge_expired_snapshots(
        snapshots_dir=daily_snaps_dir,
        expiration_time=daily_snaps_expiration_time,
        junk_dir=params.get('JUNK_DIR')
    )
    monthly_snaps_dir = os.path.join(params['BACKUP_ROOT'], 'monthly_snapshots')
    if now.day == params['MONTHLY_BACKUPS']['DAY_OF_MONTH']:
        monthly_snap = os.path.join(monthly_snaps_dir, snap_basename)
        shutil.copytree(daily_snap, monthly_snap)
        months_to_keep = params['MONTHLY_BACKUPS']['MONTHS_TO_KEEP']
        monthly_snaps_expiration_time = now - \
                datetime.timedelta(days=(31 * months_to_keep))
        purge_expired_snapshots(
            snapshots_dir=monthly_snaps_dir,
            expiration_time=monthly_snaps_expiration_time
        )
