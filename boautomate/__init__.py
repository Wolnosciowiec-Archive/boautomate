# -*- coding: utf-8 -*-

__author__ = 'Riotkit'
__email__ = 'riotkit_org@riseup.net'

import argparse
import sys
import traceback

try:
    from .boautomatelib import Boautomate
except ImportError:
    from boautomatelib import Boautomate

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node-master-url', help='Complete URL to the application for working nodes', required=True)
    parser.add_argument('--http-address', help='HTTP listen address', default='0.0.0.0')
    parser.add_argument('--http-port', help='HTTP listen port', default=8080)
    parser.add_argument('--http-prefix', help='HTTP path prefix', default='')
    parser.add_argument('--admin-token', help='Management token', default='')
    parser.add_argument('--log-path', help='Path to log file', default='./boautomate.log')
    parser.add_argument('--log-level', help='Logging level (debug, info, warning, error)', default='info')
    parser.add_argument('--docker-image', help='Docker image for the executor', default='quay.io/riotkit/boautomate-executor-base-img:latest')
    parser.add_argument('--storage',
                        help='Path to scripts or a storage. eg. filerepository://api.example.org@SOME-TOKEN, ' +
                             'file:///opt/some/directory',
                        nargs='+',
                        required=True)

    parser.add_argument('--db-string', help='Database string (SQLAlchemy compatible)',
                        default='sqlite:///var/lib/boautomate.sqlite3')

    parser.description = 'RiotKit\'s BoAutomate - A boa snake eating webhooks and processing python scripts'
    parsed = parser.parse_args()

    try:
        Boautomate(params=vars(parsed)).main()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)

    except KeyboardInterrupt:
        print('[CTRL]+[C]')
        sys.exit(0)


if __name__ == "__main__":
    main()
