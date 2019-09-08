#!/usr/bin/env python3

import sys
from pbr.version import VersionInfo

info = VersionInfo('boautomate')
with_vcs = info.version_string_with_vcs()

if "dev" in with_vcs:
    print(info.version_string() + '-SNAPSHOT')
    sys.exit(0)

print(info.version_string())
