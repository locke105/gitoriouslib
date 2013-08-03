# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mathew Odden <locke105@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import ConfigParser
import os

from gitoriouslib import gitorious

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('project')
    parser.add_argument('repo')
    parser.add_argument('--base_url')
    parser.add_argument('--email')
    parser.add_argument('--passwd')
    return parser.parse_args()

def _read_config(config_path=''):
    config = ConfigParser.SafeConfigParser()
    config.read([config_path, 'gitoriouslib.conf',
                 os.path.expanduser('~/.gitoriouslib.conf')])
    if config.has_section('gitoriouslib'):
        items = config.items('gitoriouslib')
        return dict(items)
    else:
        return {}


def _get_combined_config():
    config = _read_config()
    args_dict = vars(_parse_args())

    # override config values with args
    for key in args_dict.iterkeys():
        if args_dict[key]:
            config[key] = args_dict[key]

    for req in ['base_url', 'email', 'passwd']:
        if req not in config:
            raise Exception("Missing required option: %s" % req)

    return config


def create_repo():
    config = _get_combined_config()
    g = gitorious.Gitorious(**config)
    g.create_repo(repo_name=config['repo'],
                  project_name=config['project'])

def delete_repo():
    config = _get_combined_config()
    g = gitorious.Gitorious(**config)
    g.delete_repo(repo_name=config['repo'],
                  project_name=config['project'])
