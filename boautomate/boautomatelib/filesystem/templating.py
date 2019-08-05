
import typing
import re
from ..logging import Logger
from . import Filesystem, Syntax
from .factory import FSFactory


class Templating:
    fs: Filesystem
    fs_factory: FSFactory

    def __init__(self, fs: Filesystem, fs_factory: FSFactory):
        self.fs = fs
        self.fs_factory = fs_factory

    def inject_includes(self, content: str):
        """
            Injects file contents in place of, example:
              - @storedAtPath(boautomate/hello-world.py)
              - @storedAtFilesystem(file://./test/example-installation/configs/hello-world.conf.json)

            Works recursively, until the syntax occurs in the content.
        """

        syntax_list = [
            Syntax(
                name="@storedAtPath",
                regexp=re.compile('@storedAtPath\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\)', re.IGNORECASE),
                callback=self._stored_at_path
            ),

            Syntax(
                name="@storedOnFilesystem",
                regexp=re.compile(
                    '@storedOnFilesystem\(([A-Za-z.0-9\-_+/,:;()%!$@\[\]{}?<> ]+)\).atPath\(([A-Za-z.0-9\-_+/,:;()%!$ ]+)\)',
                    re.IGNORECASE),
                callback=self._stored_on_filesystem
            )
        ]

        for syntax in syntax_list:
            while syntax.name in content:
                Logger.debug('Templating.inject_includes() is matching %s' % syntax.name)
                match = syntax.regexp.match(content)

                if not match:
                    raise Exception('Logic error, marker "%s" found, but regexp failed to parse it' % syntax.name)

                Logger.debug('fs.Templating injecting template ' + str(match.groups()))
                content = content.replace(match.string, syntax.callback(match))

        return content

    def _stored_at_path(self, match: typing.Match):
        return self.fs.retrieve_file(match.group(1))

    def _stored_on_filesystem(self, match: typing.Match):
        return self.fs_factory.get(match.group(1)).retrieve_file(match.group(2))
