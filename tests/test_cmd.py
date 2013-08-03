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

import unittest

from gitoriouslib import cmd


class CmdTestCase(unittest.TestCase):

    def test_read_config(self):
        config = cmd._read_config('etc/gitoriouslib.conf.sample')
        self.assertEqual('http://gitorious.example.com', config['base_url'])
        self.assertEqual('someuser@example.com', config['email'])
        self.assertEqual('secret', config['passwd'])
