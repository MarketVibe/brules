from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from future import standard_library
from future.builtins import *

from brules.rules import Rule
from brules.helpers.basic import basic_step_set
from brules.helpers.html import html_step_set

from argparse import ArgumentParser
from lxml.html import parse
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import logging

log = logging.getLogger(__name__)


def run():
    import sys
    main(sys.argv[1:])


def main(argv):
    parser = ArgumentParser(description='Run some rules on a webpage')
    parser.add_argument('url')
    parser.add_argument('-d', '--dir', default='rules', required=False)
    parser.add_argument('-D', '--debug', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    rules = load_rules(args.dir)
    etree = load_url(args.url)
    run_rules(rules, etree, args.url)
    print_results(rules, args.verbose)


def load_rules(rule_dir):
    base_rule = Rule()
    base_rule.add_step_set(basic_step_set)
    base_rule.add_step_set(html_step_set)
    return base_rule.load_directory(rule_dir)


def load_url(url):
    log.debug('Loading %s', url)
    req = urlopen(url)
    if req.geturl() != url:
        log.debug('Redirected to %s', req.geturl())
    return parse(req)


def run_rules(rules, etree, url):
    for rule in rules:
        rule.run(etree=etree, url=url)


def print_results(rules, verbose):
    for rule in rules:
        status = 'Rule: {} ({})'.format(
            rule.metadata.get('name', rule.file_path),
            rule.metadata.get('id', rule.file_path))
        status = red(status) if rule.context.get('fail') else green(status)
        print(status)
        if verbose or rule.context.get('fail'):
            print(id(rule.context))
            keylen = max(len(str(k)) for k in rule.context) + 1
            for k, v in rule.context.items():
                print('  {}: {}'.format(str(k).ljust(keylen), v))


def red(txt):
    return '\033[91m' + txt + '\033[0m'


def green(txt):
    return '\033[92m' + txt + '\033[0m'

if __name__ == '__main__':
    run()