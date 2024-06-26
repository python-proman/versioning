# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE.md for more details.
# type: ignore
"""Test configuration file."""

import os

import lark

from versioning import Version, get_release_controller
from versioning.config import GRAMMAR_PATH, Config

COMMON_PATH = os.path.join(
    os.path.dirname(lark.__file__), 'grammars', 'common.lark'
)

VERSION_PATH = os.path.abspath(
    os.path.join(os.path.relpath(os.path.dirname(__file__)), '.version')
)

VERSIONING_PATH = os.path.abspath(
    os.path.join(os.path.relpath(os.path.dirname(__file__)), '.versioning')
)

PYPROJECT_PATH = os.path.abspath(
    os.path.join(os.path.relpath(os.path.dirname(__file__)), 'pyproject.toml')
)


def test_proman_source_tree(fs):
    """Test source tree loading."""
    version = Version('1.2.3')
    fs.add_real_file(VERSION_PATH)
    fs.add_real_file(VERSIONING_PATH)
    fs.add_real_file(PYPROJECT_PATH)
    config = Config(filepaths=[VERSION_PATH, VERSIONING_PATH, PYPROJECT_PATH])
    assert config.version.enable_devreleases is True
    assert config.version.enable_prereleases is True
    assert config.version.enable_postreleases is True
    assert config.version == version
    assert Version(config.lookup('version')) == version
    assert Version(config.lookup('tool.proman.version')) == version
    assert Version(config.lookup('tool.poetry.version')) == version


def test_version_release_controller(fs):
    """Test source tree loading."""
    fs.add_real_file(COMMON_PATH)
    fs.add_real_file(GRAMMAR_PATH)
    fs.add_real_file(VERSION_PATH, False)

    repo_dir = os.path.abspath(
        os.path.join(os.path.relpath(os.path.dirname(__file__)), '.gittest')
    )

    controller = get_release_controller(
        repo_dir=repo_dir, config_files=[VERSION_PATH]
    )

    version = controller.update_version(
        commit=False,
        tag=False,
        tag_name='version',
        message='test: this is a test',
        sign=False,
        dry_run=False,
    )

    config = Config(filepaths=[VERSION_PATH])

    # TODO: need to compare version with commit
    assert version == Version('1.2.3.post0')
    assert Version(config.lookup('version')) == version


def test_versioning_release_controller(fs):
    """Test source tree loading."""
    fs.add_real_file(COMMON_PATH)
    fs.add_real_file(GRAMMAR_PATH)
    fs.add_real_file(VERSIONING_PATH, False)

    repo_dir = os.path.abspath(
        os.path.join(os.path.relpath(os.path.dirname(__file__)), '.gittest')
    )

    controller = get_release_controller(
        repo_dir=repo_dir, config_files=[VERSIONING_PATH]
    )

    version = controller.update_version(
        commit=False,
        tag=False,
        tag_name='version',
        message='test: this is a test',
        sign=False,
        dry_run=False,
    )

    config = Config(filepaths=[VERSIONING_PATH])

    # TODO: need to compare version with commit
    assert version == Version('1.2.3.post0')
    assert Version(config.lookup('version')) == version


def test_pyproject_release_controller(fs):
    """Test source tree loading."""
    fs.add_real_file(COMMON_PATH)
    fs.add_real_file(GRAMMAR_PATH)
    fs.add_real_file(PYPROJECT_PATH, False)

    repo_dir = os.path.abspath(
        os.path.join(os.path.relpath(os.path.dirname(__file__)), '.gittest')
    )

    controller = get_release_controller(
        repo_dir=repo_dir, config_files=[PYPROJECT_PATH]
    )

    version = controller.update_version(
        commit=False,
        tag=False,
        tag_name='version',
        message='test: this is a test',
        sign=False,
        dry_run=False,
    )

    config = Config(filepaths=[PYPROJECT_PATH])

    # TODO: need to compare version with commit
    assert version == Version('1.2.3.post0')
    assert Version(config.lookup('tool.proman.version')) == version
    assert Version(config.lookup('tool.poetry.version')) == version
