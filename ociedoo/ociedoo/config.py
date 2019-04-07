"""This file contains tools to manage the configuration file"""

from configparser import ConfigParser
from pathlib import Path


def get_config_files(locations, name, directory=None):
    """
    Return list of paths to configuration file in :locations:.

    :param locations: list of the root path location of the confige files.
    :type locations: list<str>

    :param name: the name of the configuration file.
    :type name: str

    :param directory: the name of the directory where to store config file.
                      If :directory: is empty, it is ignored.
    :type directory: str

    """
    if directory:
        return [str(Path(l) / Path(directory) / Path(name))
                for l in locations]
    return [str(Path(l) / Path(name)) for l in locations]


class Config(ConfigParser):
    """Handel configuration of the program"""

    def __init__(self, defaults_file='', defaults=None, config_files=None,
                 default_section='general', **kw):
        """
        Create a ConfigParser with default values and specific
        configuration.

        :param defaults_file: path to a file containing a default
                              configuration.
        :param defaults: same as defaults from ConfigParser.
        :param config_files: list of path to the configuration files the
                             first is the most important, the last is
                             the less important.
        :param default_section: same as default_section from ConfigParser.
        """
        super().__init__(defaults=defaults,
                         default_section=default_section, **kw)
        # Loads default if not provided
        if not defaults:
            defaults_file_resolved = str(Path(defaults_file)
                                         .expanduser()
                                         .resolve())
            with open(defaults_file_resolved) as file:
                self.read_file(file)
        # Resolve config files
        if config_files:
            config_files_resolved = [str(Path(p).expanduser().resolve())
                                     for p in config_files
                                     if Path(p).expanduser().exists()]
        else:
            config_files_resolved = []
        # Reverse order of the config files because ConfigParser will
        # retain the last value loaded.
        config_files_resolved.reverse()
        # Loads config files
        self.config_sources = self.read(config_files_resolved)
