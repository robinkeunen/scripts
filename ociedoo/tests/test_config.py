"""Test for config.py file"""

import tempfile
from pathlib import Path

import ociedoo.config as config


def test_get_config_files():
    """
    Test for get_config_files()
    """
    locations = ['test', '~/test']
    name = 'pgrtestrc'
    directory = 'dirtest'
    res_without_dir = config.get_config_files(locations, name)
    assert res_without_dir == [str(Path('test') / Path(name)),
                               str(Path('~/test') / Path(name))]
    res_with_dir = config.get_config_files(locations, name,
                                           directory=directory)
    assert res_with_dir == [
        str(Path('test') / Path(directory) / Path(name)),
        str(Path('~/test') / Path(directory) / Path(name)),
    ]

    res_without_locations = config.get_config_files([], name)
    assert res_without_locations == []


def test_config():
    """
    Test Config class
    """
    with tempfile.TemporaryDirectory('ociedoo-test') as tmpdir:
        # Create default config file
        default = Path(tmpdir) / Path('default')
        default.write_text(
            """[odoo]
            default = value
            item = val
            foo = bar
            """
        )
        confone = Path(tmpdir) / Path('confone')
        confone.write_text(
            """[odoo]
            item = value
            foo = one
            """
        )
        conftwo = Path(tmpdir) / Path('conftwo')
        conftwo.write_text(
            """[odoo]
            foo = two
            """
        )
        confwrong = Path(tmpdir) / Path('confwrong')
        config_files = [str(confone), str(conftwo), str(confwrong)]
        cfg = config.Config(defaults_file=default, config_files=config_files)
        assert cfg.get('odoo', 'default') == 'value'
        assert cfg.get('odoo', 'item') == 'value'
        assert cfg.get('odoo', 'foo') == 'one'
