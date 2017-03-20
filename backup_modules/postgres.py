import os

from . import snapshot_utils

DEFAULT_PARAMS = {
    'DB_HOST': 'localhost',
    'DB_USER': 'postgres',
    'BACKUP_ROOT': os.environ.get('HOME', '') + '/backups/database/postgresql',
}

def execute_backup_spec(backup_spec=None):
    params = {**DEFAULT_PARAMS, **backup_spec.get('params', {})}
    snapshot_utils.default_execute_backup_spec(
        backup_spec=backup_spec,
        snapshot_generator=PostgresSnapshotGenerator(params=params),
        params=params
    )

class PostgresSnapshotGenerator(object):
    def __init__(self, params=None):
        self.params = params

    def generate_snapshot(self, *args, snapshot_dir=None, **kwargs):
        os.makedirs(snapshot_dir, exist_ok=True)
        dbs = self.list_dbs()
        for db in dbs:
            self.dump_db(db=db, target_dir=snapshot_dir)

    def list_dbs(self):
        query = ("select datname from pg_database where not "
                 "datistemplate order by datname;")
        raw_output = self.execute_query(query=query)
        return [line.strip() for line in raw_output.split('\n') if line]

    def execute_query(self, query=None):
        psql_cmd = (
            'psql {auth_params} -At -c \'{query}\' postgres'
        ).format(
            auth_params=self.generate_pg_auth_params(),
            query=query
        )
        completed_proc = snapshot_utils.run_cmd(cmd=psql_cmd)
        output = completed_proc.stdout.decode('utf-8')
        return output

    def generate_pg_auth_params(self):
        return '-h "{db_host}" -U "{db_user}"'.format(
            db_host=self.params['DB_HOST'],
            db_user=self.params['DB_USER']
        )

    def dump_db(self, db=None, target_dir=None):
        dump_file = os.path.join(target_dir, '{db}.sql.gz'.format(db=db))
        partial_file = dump_file + '.partial'
        dump_cmd = (
            'pg_dump -Fp {auth_params} "{db}" | gzip > {partial_file}'
            ' && mv {partial_file} {dump_file}'
        ).format(
            auth_params=self.generate_pg_auth_params(),
            db=db,
            partial_file=partial_file,
            dump_file=dump_file
        )
        snapshot_utils.run_cmd(cmd=dump_cmd)
