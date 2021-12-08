# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
# type: ignore
"""Test configuration file."""

import os

from versioning import get_release_controller, get_source_tree, Version
from versioning.config import GRAMMAR_PATH

VERSIONING_PATH = os.path.abspath(
    os.path.join(
        os.path.relpath(os.path.dirname(__file__)),
        '.versioning',
    )
)

PYPROJECT_PATH = os.path.abspath(
    os.path.join(
        os.path.relpath(os.path.dirname(__file__)),
        'pyproject.toml',
    )
)
print(PYPROJECT_PATH)


def test_proman_source_tree(fs):
    """Test source tree loading."""
    version = Version('1.2.3')
    fs.add_real_file(VERSIONING_PATH)
    fs.add_real_file(PYPROJECT_PATH)
    config = get_source_tree(config_files=[VERSIONING_PATH, PYPROJECT_PATH])
    assert config.version.enable_devreleases is True
    assert config.version.enable_prereleases is True
    assert config.version.enable_postreleases is True
    assert config.version == version
    assert Version(config.retrieve('.proman.version')) == version
    assert Version(config.retrieve('.tool.proman.version')) == version
    assert Version(config.retrieve('.tool.poetry.version')) == version


def test_proman_release_controller(fs):
    """Test source tree loading."""
    import lark

    COMMON_PATH = os.path.join(
        os.path.dirname(lark.__file__), 'grammars', 'common.lark'
    )
    fs.add_real_file(COMMON_PATH)
    fs.add_real_file(GRAMMAR_PATH)
    fs.add_real_file(VERSIONING_PATH, False)
    fs.add_real_file(PYPROJECT_PATH, False)

    repo_dir = os.path.abspath(
        os.path.join(
            os.path.relpath(os.path.dirname(__file__)), '.gittest'
        )
    )

    controller = get_release_controller(
        repo_dir=repo_dir,
        config_files=[VERSIONING_PATH, PYPROJECT_PATH],
    )

    version = controller.bump_version(
        commit=False,
        tag=False,
        tag_name='version',
        message='this is a test',
        sign=False,
        dry_run=False,
    )

    config = get_source_tree(config_files=[VERSIONING_PATH, PYPROJECT_PATH])

    # TODO: need to compare version with commit
    assert version == Version('1.2.3.post0')
    assert Version(config.retrieve('.proman.version')) == version
    assert Version(config.retrieve('.tool.proman.version')) == version
    assert Version(config.retrieve('.tool.poetry.version')) == version
