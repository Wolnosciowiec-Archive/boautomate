#!/usr/bin/env python3

import os
import subprocess

cmdline = ''

MAPPING = {
    'DB_STRING': ['--db-string={{ VALUE }}', '--db-string=sqlite:///db.sqlite3'],
    'NODE_MASTER_URL': ['--node-master-url={{ VALUE }}', '--node-master-url=http://localhost:8080'],
    'HTTP_PORT': ['--http-port={{ VALUE }}', '--http-port=8080'],
    'LOCAL_PATH': ['--local-path={{ VALUE }}', '--local-path=./test/example-installation/boautomate-local'],
    'LOG_LEVEL': ['--log-level={{ VALUE }}', '--log-level=debug'],
    'LOG_PATH': ['--log-path={{ VALUE }}', '--log-path=boautomate-test.log']
}

for env_name, opts in MAPPING.items():
    env_value = os.getenv(env_name)

    if env_value is not None:
        cmdline += ' ' + opts[0].replace('{{ VALUE }}', env_value)
        continue

    # defaults
    cmdline += ' ' + opts[1]


subprocess.call('boautomate ' + cmdline, shell=True)
