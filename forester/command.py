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
    _options = [
            ('verbose', '-v', options.COUNT_PARAM, dict(help="Increase verbosity")),
            ]

    def addParameters(self, argDef):
        command.AbstractCommand.addParameters(self, argDef)
        self.addLocalParameters(argDef)

    def addLocalParameters(self, argDef):
        for opt in self._options:
            optName, rest = opt[0], opt[1:]
            argDef[optName] = rest

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

    _options = ForesterCommand._options + [
            ('name', options.ONE_PARAM, dict(help='User Name used for git')),
            ('email', options.ONE_PARAM, dict(help='Email used for git')),
            ('common-aliases', options.NO_PARAM, dict(help='Setup common aliases for git')),
            ('cfgfile', options.ONE_PARAM, dict(help='Path to forestrc config file')),
            ('subdir', options.ONE_PARAM, dict(help='Top Level Sub Directory for all git checkouts')),
            ('forest', options.ONE_PARAM, dict(help='Name of forest to add to the config')),
            ('branch', options.ONE_PARAM, dict(help='Prefered branch of forest to add to the config')),
            ('wms', options.NO_PARAM, dict(help='Set forest as WMS forest')),
            ('wmsbase', options.ONE_PARAM, dict(help='Base url for WMS service')),
            ('wmspath', options.ONE_PARAM, dict(help='Path for the wms forest')),
            ]


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
    WithPull = False
    WithPush = False
    commands = ['clone']
    help = 'Clone git forest from a control source'
    paramsHelp = '[forest]...'
    _options = ForesterCommand._options + [
            ('cfgfile', options.ONE_PARAM, dict(help='Path to forestrc config file')),
            ('ask', options.NO_PARAM, dict(help='Ask before cloning a git repo')),
            ('readonly', options.NO_PARAM, dict(help='Do not mangle read only git repo uri')),
            ('dry-run' , options.NO_PARAM, dict(help='List the head instead of cloning git repo')),
            ('exclude' , options.MULT_PARAM, dict(help='Skip these repos')),
            ]

    requireConfig = True

    def shouldRun(self):
        if not self.forests:
            logger.error('forest command requires at least one forest')
            return False
        return True

    def runCommand(self, cfg, argSet, params, **kw):
        self.cfg = cfg
        self.cfgfile = argSet.pop('cfgfile', None)
        self.branch = argSet.pop('branch', None)
        self.excludes = argSet.pop('exclude', None)
        self.ask = argSet.pop('ask', False)
        self.readonly = argSet.pop('readonly', False)
        self.test = argSet.pop('dry-run', False)
    
        self.forests = params[2:]

        
        if not self.shouldRun():
            logger.error('clone will not run, exiting.')
            sys.exit(2)


        for forest in self.forests:
            try:
                _skid = skidder.Skidder(forest = forest,
                    cfgfile= self.cfgfile,
                    base = None,
                    path = None,
                    ask=self.ask,
                    readonly=self.readonly,
                    test = self.test,
                    )
            except skidder.InvalidForest:
                logger.error("Forest %s is not defined", forest)
                continue
            _skid.main(otherBranch=self.branch, withPull=self.WithPull,
                    withPush=self.WithPush)

class PullCommand(CloneCommand):
    WithPull = True
    commands = ['pull']
    help = 'Pull git forest from a control source'
    paramsHelp = '[forest]...'

class MergeCommand(PullCommand):
    WithPush = True
    commands = ['merge']
    help = 'Merge git forest with branch'
    paramsHelp = '[forest]...'
    _options = PullCommand._options + [
            ('branch', options.ONE_PARAM, dict(help='Branch to merge with')),
            ]

    def shouldRun(self):
        if not super(MergeCommand, self).shouldRun():
            return False
        if not self.branch:
            logger.error("--branch is required")
            return False
        return True
