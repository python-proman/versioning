# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide CLI management.'''

from argufy import Parser

from proman_releases.cli import release, version


def main() -> None:
    '''Provide CLI for git-tools.'''
    parser = Parser(command_type='subcommand')
    parser.add_commands(release)
    parser.add_commands(version)
    parser.dispatch()


if __name__ == '__main__':
    main()
