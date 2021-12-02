
# license: MPL-2.0, see LICENSE for more details.
"""Manage version numbers."""

# import logging
from typing import Any, List, Optional, Tuple, Union

from packaging.version import Version as PackageVersion
from packaging.version import _cmpkey, _parse_local_version, _Version
from transitions import Machine


class Version(PackageVersion):
    """Provide PEP440 compliant versioning."""

    def __init__(self, version: str, **kwargs: Any) -> None:
        """Initialize version object."""
        # self.kind = kwargs.pop('version_system', 'semver')
        super().__init__(version=version)

        # TODO: transitions here should be populated by VCS workflow
        self.enable_devreleases = kwargs.get('enable_devreleases', True)
        self.enable_prereleases = kwargs.get('enable_prereleases', True)
        self.enable_postreleases = kwargs.get('enable_postreleases', True)

        self.machine = Machine(
            self, states=self.states, initial=self.release_type
        )

        # dev-releases
        self.machine.add_transition(
            trigger='start_devrelease',
            source=['final', 'release', 'post'],
            dest='development',
            before='new_devrelease',
            conditions=['devreleases_enabled'],
        )

        # pre-releases
        self.machine.add_transition(
            trigger='start_alpha',
            source=['final', 'development', 'post'],
            dest='alpha',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )
        self.machine.add_transition(
            trigger='start_beta',
            source='alpha',
            dest='beta',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )
        self.machine.add_transition(
            trigger='start_release',
            source='beta',
            dest='release',
            before='new_prerelease',
            conditions=['prereleases_enabled'],
        )

        # final release
        self.machine.add_transition(
            trigger='finish_release',
            source=['development', 'release'],
            dest='final',
            before='finalize_release',
        )

        # post-releases
        self.machine.add_transition(
            trigger='start_postrelease',
            source='final',
            dest='post',
            before='new_postrelease',
            conditions=['postreleases_enabled'],
        )

    @property
    def states(self) -> List[str]:
        """List all states."""
        states = ['final']
        if self.enable_devreleases:
            states += ['development']
        if self.enable_prereleases:
            states += ['alpha', 'beta', 'release']
        if self.enable_postreleases:
            states += ['post']
        return states

    @property
    def devreleases_enabled(self) -> bool:
        """Check if devreleases are enabled."""
        return self.enable_devreleases

    @property
    def prereleases_enabled(self) -> bool:
        """Check if prereleases are enabled."""
        return self.enable_prereleases

    @property
    def postreleases_enabled(self) -> bool:
        """Check if postreleases are enabled."""
        return self.enable_postreleases

    @property
    def release_type(self) -> str:
        """Get the current state of package release."""
        if self.is_devrelease:
            state = 'development'
        elif self.is_prerelease and self.pre:
            if self.pre[0] == 'a':
                return 'alpha'
            elif self.pre[0] == 'b':
                return 'beta'
            elif self.pre[0] == 'rc':
                return 'release'
        elif self.is_postrelease:
            state = 'post'
        else:
            state = 'final'
        return state

    def __update_version(
        self,
        epoch: Optional[int] = None,
        release: Optional[Tuple[Any, ...]] = None,
        pre: Optional[Tuple[str, int]] = None,
        post: Optional[Union[Tuple[str, int], str]] = None,
        dev: Optional[Tuple[str, int]] = None,
        local: Optional[str] = None,
    ) -> None:
        """Update the internal version state."""
        if not (epoch or release):
            pre = pre or self.pre
            post = post or self.post
            dev = dev or self.dev

        self._version = _Version(
            epoch=epoch or self.epoch,
            release=release or self.release,
            pre=pre,
            post=post,
            dev=dev,
            local=_parse_local_version(local) if local else None,
        )

        self._key = _cmpkey(
            self._version.epoch,
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
            self._version.local,
        )

    def bump_epoch(self) -> None:
        """Update epoch releaes for version system changes."""
        self.__update_version(epoch=self.epoch + 1)
        self.machine.set_state('final')

    def bump_major(self) -> None:
        """Update major release to next version number."""
        self.__update_version(release=(self.major + 1, 0, 0))
        self.machine.set_state('final')

    def bump_minor(self) -> None:
        """Update minor release to next version number."""
        self.__update_version(release=(self.major, self.minor + 1, 0))
        self.machine.set_state('final')

    def bump_micro(self) -> None:
        """Update micro release to next version number."""
        self.__update_version(release=(self.major, self.minor, self.micro + 1))

    def __bump_version(self, kind: str) -> None:
        """Bump version based on version kind."""
        if kind == 'major':
            self.bump_major()
        if kind == 'minor':
            self.bump_minor()
        if kind == 'micro':
            self.bump_micro()

    def new_local(self, name: str = 'build') -> None:
        """Create new local version instance number."""
        if self.local is None:
            self.__update_version(local=f"{name}.0")
        elif self.local is not None:
            local = self.local.split('.')
            if local[-1].isdigit():
                local[-1] = str(int(local[-1]) + 1)
            self.__update_version(local='.'.join(local))

    def new_devrelease(self, kind: str = 'minor') -> None:
        """Update to the next development release version number."""
        if self.dev is None:
            self.__bump_version(kind)
            dev = ('dev', 0)
        elif self.dev is not None:
            # XXX: stupid pypa bug
            if type(self.dev) is int:
                dev = ('dev', self.dev + 1)  # type: ignore
            else:
                dev = (self.dev[0], self.dev[1] + 1)
        self.__update_version(dev=dev)

    def new_prerelease(
        self, kind: Optional[str] = None, next_release: bool = False
    ) -> None:
        """Update to next prerelease version type."""
        if self.pre is None:
            if not self.enable_devreleases:
                self.__bump_version(kind or 'minor')
            pre = ('a', 0)
        elif self.pre is not None and not next_release:
            pre = (self.pre[0], self.pre[1] + 1)
        else:
            if self.pre[0] == 'a':
                pre = ('b', 0)
            elif self.pre[0] == 'b':
                pre = ('rc', 0)
        self.__update_version(pre=pre)

    def new_postrelease(self) -> None:
        """Update to next prerelease version type."""
        if self.release_type == 'final':
            self.__update_version(post=('post', 0))
        elif self.post is not None:
            if type(self.post) is tuple:
                post = (self.post[0], self.post[1] + 1)
            else:
                post = ('post', self.post + 1)  # type: ignore
            self.__update_version(post=post)

    def finalize_release(self) -> None:
        """Update to next prerelease version type."""
        if self.is_devrelease or self.is_prerelease:
            self.__update_version(release=(self.major, self.minor, self.micro))
