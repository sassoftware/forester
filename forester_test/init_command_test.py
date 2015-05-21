#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



import forester
import sys
import unittest

from forester import command
from forester import utils
from testutils import mock

class InitCommandTest(unittest.TestCase):
    def setUp(self):
        sys.exit = mock.MockObject()
        command.logger = mock.MockObject()
        utils.InitialSetup = mock.MockObject()

        self.init = mock.MockInstance(command.InitCommand())
        self.init._mock.enableByDefault()
        self.init._mock.enableMethod('runCommand')
        self.init._mock.enableMethod('shouldRun')

    def testInitRequiresNameOrSubdir(self):
        self.init.runCommand(object(), {}, object())
        command.logger.error._mock.assertCalled('init command requires at'
                ' least one --name or one --subdir')
        sys.exit._mock.assertCalled(2)

    def testInitAcceptsName(self):
        args = {'name':'foo'}
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertNotCalled()
        sys.exit._mock.assertNotCalled()

    def testInitAcceptsSubdir(self):
        args = {'subdir':'/home/user/foo'}
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertNotCalled()
        sys.exit._mock.assertNotCalled()

    def testWmsRequiresBaseAndPath(self):
        args = {'name':'foo', 'wms':True}
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertCalled('init command with --wms'
                ' option requires both --wmsbase and --wmspath options')
        sys.exit._mock.assertCalled(2)

    def testWmsRequiresBase(self):
        args = {'name':'foo',
                'wms':True,
                'wmspath':'example/foo',
                }
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertCalled('init command with --wms'
                ' option requires both --wmsbase and --wmspath options')
        sys.exit._mock.assertCalled(2)

    def testWmsRequiresPath(self):
        args = {'name':'foo',
                'wms':True,
                'wmsbase':'http://example.com',
                }
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertCalled('init command with --wms'
                ' option requires both --wmsbase and --wmspath options')
        sys.exit._mock.assertCalled(2)

    def testWmsAcceptsBaseAndPath(self):
        args = {'name':'foo',
                'wms':True,
                'wmsbase':'http://example.com',
                'wmspath':'example/foo',
                }
        self.init.runCommand(object(), args, object())
        command.logger.error._mock.assertNotCalled()
        sys.exit._mock.assertNotCalled()

