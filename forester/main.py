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


import errno
import logging
import os
import sys

from conary.lib import log as cny_log
from conary.lib import mainhandler
from conary.lib import util as conary_util

from forester import command
from forester import config
from forester import constants
from forester import errors

logger = logging.getLogger(__name__)


class ForesterMain(mainhandler.MainHandler):

    name = 'forester'
    version = constants.version

    abstractCommand = command.ForesterCommand
    configClass = config.ForesterConfiguration
    commandList = [
        command.HelpCommand,
        command.ConfigCommand,
        command.CloneCommand,
        command.PullCommand,
        command.MergeCommand,
        command.PushCommand,
        command.InitCommand,
        command.CheckoutCommand,
        command.BranchCommand,
        ]

    setSysExcepthook = False

    def _getParserFlags(self, thisCommand):
        # We need to disable Conary's handling of --verbose
        ret = super(ForesterMain, self)._getParserFlags(thisCommand)
        ret['addVerboseOptions'] = False
        return ret

    def configureLogging(self, logFile, verbosity):
        logDir = os.path.dirname(logFile)
        if not logDir:
            # Initial configuration; don't even bother
            return
        conary_util.mkdirChain(logDir)
        if verbosity == 0:
            consoleLevel = fileLevel = logging.WARN
        elif verbosity == 1:
            consoleLevel = fileLevel = logging.INFO
        else:
            consoleLevel = fileLevel = logging.DEBUG
        cny_log.setupLogging(
            logPath=logFile,
            consoleLevel=consoleLevel,
            fileLevel=fileLevel,
            logger='forester',
            )

    def runCommand(self, command, cfg, argSet, *args, **kw):
        verbosity = 0
        if cfg.debugMode:
            verbosity = 2
        # Command line trumps config file
        verbosity = argSet.get('verbose', verbosity)
        self.configureLogging(cfg.logFile, verbosity)
        logger.info("Running command: %s", command.commands[0])
        response = mainhandler.MainHandler.runCommand(self, command, cfg,
                                                      argSet, *args, **kw)
        logger.info("Command finished: %s", command.commands[0])
        return response


def _main(argv, MainClass):
    """
    Wrapper method that handles all remaining uncaught exceptions from
    forester.

    @param argv: standard argument vector
    @param MainClass: class object that implements a main() method.
    """
    if argv is None:
        argv = sys.argv
    #pylint: disable-msg=E0701
    # pylint complains about except clauses here because we sometimes
    # redefine debuggerException
    debuggerException = Exception
    try:
        argv = list(argv)
        debugAll = '--debug-all' in argv
        if debugAll:
            argv.remove('--debug-all')
        else:
            debuggerException = errors.ForesterError
        sys.excepthook = errors.genExcepthook(debug=debugAll,
                                              debugCtrlC=debugAll)
        rc = MainClass().main(argv, debuggerException=debuggerException)
        if rc is None:
            return 0
        return rc
    except errors.ForesterError, e:
        print e
        return 1
    except debuggerException, e:
        raise
    except IOError, e:
        # allow broken pipe to exit
        if e.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        return 1
    return 0


def main(argv=None):
    """
    Python hook for starting forester from the command line.
    @param argv: standard argument vector
    """
    return _main(argv, ForesterMain)
