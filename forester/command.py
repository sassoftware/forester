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


import logging
import sys

from conary.lib import command, options

from forester import skidder
from forester import utils

logger = logging.getLogger(__name__)


class ForesterCommand(command.AbstractCommand):

    def addParameters(self, argDef):
        command.AbstractCommand.addParameters(self, argDef)
        argDef['quiet'] = options.NO_PARAM
        argDef['debug-logging'] = options.NO_PARAM

    def runCommand(self, *args, **kw):
        pass


class HelpCommand(ForesterCommand):
    """
    Displays help about this program or commands within the program.
    """
    commands = ['help']
    help = 'Display help information'

    def runCommand(self, cfg, argSet, args, **kwargs):
        command, subCommands = self.requireParameters(args, allowExtra=True)
        if subCommands:
            command = subCommands[0]
            commands = self.mainHandler._supportedCommands
            if not command in commands:
                print >> sys.stderr, "%s: no such command: '%s'" % (
                    self.mainHandler.name, command)
                sys.exit(1)
            print >> sys.stderr, commands[command].usage()
        else:
            print >> sys.stderr, self.mainHandler.usage()


class ConfigCommand(ForesterCommand):
    commands = ['config']
    help = 'Display the current configuration'

    def runCommand(self, cfg, argSet, args, **kwargs):
        cfg.setDisplayOptions(hidePasswords=True,
                              showContexts=False,
                              prettyPrint=True,
                              showLineOrigins=False)
        if argSet:
            return self.usage()
        if (len(args) > 2):
            return self.usage()
        else:
            cfg.display()



class InitCommand(ForesterCommand):
    commands = ['init']
    help = 'Init working directories'

    def addParameters(self, argDef):
        ForesterCommand.addParameters(self, argDef)
        argDef['name'] = options.ONE_PARAM
        argDef['email'] = options.ONE_PARAM
        argDef['common-aliases'] = options.NO_PARAM
        argDef['subdir'] = options.ONE_PARAM
        argDef['cfgfile'] = options.ONE_PARAM
        argDef['forest'] = options.ONE_PARAM
        argDef['branch'] = options.ONE_PARAM
        argDef['wms'] = options.NO_PARAM
        argDef['wmsbase'] = options.ONE_PARAM 
        argDef['wmspath'] = options.ONE_PARAM

    def shouldRun(self):
        if not self.name and not self.subdir:
            logger.error('init command requires at least one --name or one --subdir')
            return False
        return True

    def runCommand(self, cfg, argSet, params, **kw):
        self.cfg = cfg
        self.name = argSet.pop('name', None)
        self.email = argSet.pop('email', None)
        self.aliases = argSet.pop('common-aliases', None)
        self.subdir = argSet.pop('subdir', None)
        self.cfgfile = argSet.pop('cfgfile', None)
        self.forest = argSet.pop('forest', None)
        self.branch = argSet.pop('branch', None)
        self.wms = argSet.pop('wms', False)
        self.wmsbase = argSet.pop('wmsbase', None)
        self.wmspath = argSet.pop('wmspath', None)
        

        if not self.shouldRun():
            logger.info('init will not run, exiting.')
            sys.exit(2)
        
        iSetup = utils.InitialSetup()

        iSetup.initialSetup(
                self.name,
                self.email,
                self.aliases,
                self.subdir,
                self.cfgfile,
                self.forest,
                self.branch,
                self.wms,
                self.wmsbase,
                self.wmspath,
                )


class CloneCommand(ForesterCommand):
    commands = ['clone']
    help = 'Clone git forest from a control source'

    def addParameters(self, argDef):
        ForesterCommand.addParameters(self, argDef)
        argDef['forest'] = options.ONE_PARAM
        argDef['branch'] = options.ONE_PARAM
        argDef['excludes'] = options.MULT_PARAM
        argDef['cfg'] = options.ONE_PARAM
        argDef['dir'] = options.ONE_PARAM
        argDef['cachedir'] = options.ONE_PARAM
        argDef['dry-run'] = options.NO_PARAM
        argDef['ask'] = options.NO_PARAM
        argDef['base'] = options.ONE_PARAM
        argDef['path'] = options.ONE_PARAM
        argDef['control-file'] = options.ONE_PARAM
        argDef['control-uri'] = options.ONE_PARAM

    def shouldRun(self):
        if self.forest and self.cfgfile:
            return True
        logger.error('forest command requires at least --forest or one --cfgfile')
        return False


    def runCommand(self, cfg, argSet, params, **kw):
        self.cfg = cfg
        self.cfgfile = argSet.pop('cfgfile', None)
        self.forest = argSet.pop('forest', None)
        self.branch = argSet.pop('branch', None)
        self.excludes = argSet.pop('excludes', None)
        self.subdir = argSet.pop('subdir', None)
        self.base = argSet.pop('base', None)
        self.path = argSet.pop('path', None)
        self.controlfile = argSet.pop('control-file', None)
        self.controluri = argSet.pop('control-uri', None)
        self.cachedir = argSet.pop('cachedir', None)
        self.ask = argSet.pop('ask', False)
        self.test = argSet.pop('dry-run', False)


        _skid = skidder.Skidder(forest = self.forest, 
                                cfgfile= self.cfgfile, 
                                base = self.base, 
                                path = self.path, 
                                branch = self.branch, 
                                ask=self.ask,
                                test = self.test,
                            )
        _skid.main()



