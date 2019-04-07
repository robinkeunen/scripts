# Copyright 2018 Coop IT Easy SCRLfs (<http://coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This is a wrapper for Odoo to update modules when there is multiple
databases.

Maintainer: Rémy Taymans <remy@coopiteasy.be>

Usage:
    See help (--help).
"""
import argparse
import os
import signal
import sys
from pathlib import Path

import sh

import ociedoo.config as config


# Path for default value for config file
PGRNAME = 'ociedoo'
DEFAULTSPATH = str(Path(__file__).parent / Path('defaults'))
DEFAULT_CONF = str(Path(DEFAULTSPATH) / Path(PGRNAME+'rc.spec'))

# Environement var
# TODO: For XDG, a library like xdg or pyxdg may be used
XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME',
                                 str(Path.home() / Path('.config')))
XDG_CONFIG_DIRS = (os.environ.get('XDG_CONFIG_DIRS',
                                  str(Path('/etc/xdg')))).split(':')
OCIEDOO_CONF = os.environ.get('OCIEDOO_CONF', '')

# Config files
CONF_FILES = (
    [OCIEDOO_CONF]
    + config.get_config_files([XDG_CONFIG_HOME], PGRNAME+'rc',
                              directory=PGRNAME)
    + config.get_config_files(['~'], '.'+PGRNAME+'rc')
    + config.get_config_files(XDG_CONFIG_DIRS, PGRNAME+'rc',
                              directory=PGRNAME)
    + config.get_config_files(['/etc'], PGRNAME+'rc',
                              directory=PGRNAME)
)


def init_parser():
    """Initialise the parser"""
    # Arguments (-h/--help is automatically added)
    parser = argparse.ArgumentParser(
        description=("This is a wrapper for Odoo to update modules "
                     "when there is multiple databases.")
    )
    parser.add_argument('databases',
                        help="database names separated by comas or 'all'")
    parser.add_argument('odoo_args',
                        nargs=argparse.REMAINDER,
                        help="odoo command line arguments")
    return parser


def get_all_db(db_user=''):
    """Get all databases that belongs to :db_user"""
    psql_out = sh.grep(sh.psql('-l'), db_user).strip()
    psql_out_lines = psql_out.split('\n')
    db = [line.split('|')[0].strip() for line in psql_out_lines]
    return db


def is_odoo_running(daemon_name=''):
    """Check if an odoo daemon is running or not."""
    active = sh.systemctl(
        "show", "--property", "ActiveState", daemon_name,
        _tty_out=False,
    ).strip()
    return active.split('=')[-1] == "active"


def main():
    """Program starts here"""
    args = init_parser().parse_args()
    cfg = config.Config(defaults_file=DEFAULT_CONF,
                        config_files=CONF_FILES)

    db_user = cfg.get("odoo", "database_user")
    odoo_path = cfg.get("odoo", "binary_path")
    odoo_conf_path = cfg.get("odoo", "config_path")
    odoo_daemon_name = cfg.get("odoo", "daemon_name")
    odoo_working_dir = cfg.get("odoo", "working_directory")

    if args.databases.strip() == "all":
        dbs = get_all_db(db_user)
    else:
        dbs = [db.strip() for db in args.databases.split(',')]

    if is_odoo_running(odoo_daemon_name):
        print("Error: Odoo service is running. Stop it before update.")
        print("To do so, run in root: systemctl stop %s" % odoo_daemon_name)
        sys.exit(1)

    # Change working directory
    os.chdir(odoo_working_dir)

    # Create odoo cmd
    try:
        odoo_cmd = sh.Command(odoo_path)
    except sh.CommandNotFound:
        print("Error: Command %s not found" % odoo_path)
        sys.exit(1)

    # Run odoo cmd for each database
    for db in dbs:
        odoo_process = odoo_cmd(
            '-c', odoo_conf_path,
            '--db-filter', db,
            '-d', db,
            '--logfile', '/proc/self/fd/1',
            '--stop-after-init',
            *args.odoo_args,
            _out=sys.stdout.buffer,
            _err=sys.stderr.buffer,
            _bg=True,
        )
        print("\nRunning : %s\n" % odoo_process.ran)
        try:
            odoo_process.wait()
        except KeyboardInterrupt:
            odoo_process.signal(signal.SIGINT)
            print("W: Exiting… Press CTRL-C again to force the shutdown.")
            try:
                odoo_process.wait()
            except KeyboardInterrupt:
                odoo_process.kill()
                print("W: Forced exit. Program stops here.")
                sys.exit(1)
            odoo_process.kill()
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
