# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: LGPL-3.0, see LICENSE for more details.
'''Provide documentation tasks.'''

from invoke import Context, task


@task
def lint(ctx):  # type: (Context) -> None
    '''Check code for documentation errors.'''
    ctx.run('pydocstyle')


@task
def coverage(ctx):  # type: (Context) -> None
    '''Ensure all code is documented.'''
    ctx.run('docstr-coverage **/*.py')


@task(pre=[lint], post=[coverage])
def test(ctx):  # type: (Context) -> None
    '''Test documentation build.'''
    # TODO: should be doctest
    ctx.run('mkdocs build')


@task
def build(ctx):  # type: (Context) -> None
    '''Build documentation site.'''
    ctx.run('mkdocs build')


@task
def publish(ctx):  # type: (Context) -> None
    '''Publish project documentation.'''
    ctx.run('mkdocs gh-deploy')
