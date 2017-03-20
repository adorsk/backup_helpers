## Summary
This is a set of scripts to help with creating local backups. Note that it does *not* save these backups to an external location. You must set that up yourself.

## Setup
1. Clone repo.
2. Copy `config_example.py` to `config.py`.
3. Edit settings/backup specs in config.py.
4. Add to crontab to run periodically:
  1. (on mac) `EDITOR=vi crontab -e`
  2. Add a line like this: `37 2 * * * /bin/bash -l -c '/<path>/<to>/<this>/<dir>/make_backups.py' > /tmp/backups.log` . This will run the backups script every day at 02:37.
  3. Confirm that your crontab was changed by running `crontab -l`. You should see the line you added in the output.
5. Copy your ~/backups folder to an external location.
6. Periodically check your backups, to make sure they are capturing what you want.
