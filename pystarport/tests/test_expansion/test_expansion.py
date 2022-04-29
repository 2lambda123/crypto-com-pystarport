import os
from pathlib import Path

import pytest
import yaml
from deepdiff import DeepDiff

from pystarport.expansion import expand_jsonnet, expand_yaml


def _get_base_config():
    return yaml.safe_load(open(Path(__file__).parent / "base.yaml"))


@pytest.mark.parametrize("type", [".yaml", ".jsonnet"])
def test_expansion(type):
    test_yaml = type == ".yaml"
    print("type", type, test_yaml)
    parent = Path(__file__).parent
    cronos_has_dotenv = parent / ("cronos_has_dotenv" + type)
    cronos_no_dotenv = parent / ("cronos_no_dotenv" + type)
    cronos_has_posix_no_dotenv = parent / ("cronos_no_dotenv" + type)
    baseConfig = _get_base_config()
    # `expand_yaml` is backward compatible, not expanded, and no diff
    if test_yaml:
        func = expand_yaml
    else:
        func = expand_jsonnet

    config = func(cronos_no_dotenv, None)
    assert baseConfig == config

    # `expand_yaml` is expanded but no diff
    config = func(cronos_has_dotenv, None)
    assert not DeepDiff(
        baseConfig,
        config,
        ignore_order=True,
    )

    # overriding dotenv with relative path is expanded and has diff)
    dotenv = "dotenv1"
    config = func(cronos_has_dotenv, dotenv)
    assert DeepDiff(
        baseConfig,
        config,
        ignore_order=True,
    ) == {
        "values_changed": {
            "root['cronos_777-1']['validators'][0]['mnemonic']": {
                "new_value": "good",
                "old_value": "visit craft resemble online window solution west chuckle "
                "music diesel vital settle comic tribe project blame bulb armed flower "
                "region sausage mercy arrive release",
            }
        }
    }

    # overriding dotenv with absolute path is expanded and has diff
    dotenv = os.path.abspath("test_expansion/dotenv1")
    config = func(cronos_has_dotenv, dotenv)
    assert DeepDiff(
        baseConfig,
        config,
        ignore_order=True,
    ) == {
        "values_changed": {
            "root['cronos_777-1']['validators'][0]['mnemonic']": {
                "new_value": "good",
                "old_value": "visit craft resemble online window solution west chuckle "
                "music diesel vital settle comic tribe project blame bulb armed flower "
                "region sausage mercy arrive release",
            }
        }
    }

    # overriding dotenv with absolute path is expanded and no diff
    dotenv = os.path.abspath("test_expansion/dotenv")
    config = func(cronos_has_posix_no_dotenv, dotenv)
    assert not DeepDiff(
        baseConfig,
        config,
        ignore_order=True,
    )
