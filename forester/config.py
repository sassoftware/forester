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


import os
import time

from conary.build.macros import Macros
from conary.lib import cfg
from conary.lib.cfgtypes import CfgList 
from conary.lib.cfgtypes import CfgString 
from conary.lib.cfgtypes import CfgDict 
from conary.lib.cfgtypes import CfgBool
from conary.lib.cfgtypes import CfgType, ParseError
from conary.deps import deps


DEFAULT_PATH = ['./.foresterrc']


class CfgDependency(CfgType):

    def parseString(self, val):
        return deps.parseDep(val)

    def format(self, val, displayOptions=None):
        return str(val)



class ForestTargetSection(cfg.ConfigSection):
    '''
    Forest directory configuration:
    [forrest:appengine]
    '''

    ForestName              = CfgString
    ForestBranch            = CfgString
    ForestControlFile       = CfgString
    ForestControlUri        = CfgString
    ForestControlPath       = CfgString
    ForestDescription       = CfgString
    ForestExcludes          = CfgList(CfgString)
    ForestTest              = (cfg.CfgBool, False)
    ForestSubDir            = CfgString
    ForestCacheDir          = CfgString
    ForestControlType       = CfgString

    def getForestUri(self):
        return os.path.join(self.ForestBaseUri, self.ForestName)



class MainConfig(cfg.SectionedConfigFile):
    '''
    Main Configuration for program
    '''
    macros                  = CfgDict(CfgString)
    override                = CfgDict(CfgString)
    configPath              = CfgString
    logging                 = CfgBool
    logFile                 = CfgString
    lockFile                = CfgString
    branch                  = CfgString

    BuildTemplateDisplayNames = CfgDict(CfgString)

    # custom handling of sections
    _sectionMap = {
                    'forest' : ForestTargetSection, 
                }

    def __init__(self):
        cfg.SectionedConfigFile.__init__(self)
        self._macros = None

    def read(self, path, **kwargs):
        return cfg.SectionedConfigFile.read(self, path, **kwargs)

    def setSection(self, sectionName):
        if not self.hasSection(sectionName):
            found = False
            for name, cls in self._sectionMap.iteritems():
                if sectionName == name or sectionName.startswith(name + ':'):
                    found = True
                    self._addSection(sectionName, cls(self))
            if not found:
                raise ParseError('Unknown section "%s"' % sectionName)
        self._sectionName = sectionName
        return self._sections[sectionName]

    def getMacros(self):
        if self._macros is None:
            macros = Macros(self.macros)
            macros.update(self.override)
            macros['start_time'] = time.strftime('%Y%m%d_%H%M%S')
            macros['target_label'] = self.targetLabel % macros
            self._macros = macros
        return self._macros

class ForesterConfiguration(MainConfig):

    userName                    = CfgString
    userEmail                   = CfgString
    useAliases                  = (cfg.CfgBool, False)
    debugMode                   = (cfg.CfgBool, False)
    testOnly                    = (cfg.CfgBool, False)
    logFile                     = (cfg.CfgString, 'forester.log')
    lockFile                    = (cfg.CfgString, 'forester.lock')
    tmpDir                      = (cfg.CfgString, 'tmp')
    defaultCacheDir             = (cfg.CfgString, 'cachedir')
    defaultBranch               = (cfg.CfgString, 'master')
    defaultSubDir               = (cfg.CfgString, 'git')
    defaultConfigFile           = (cfg.CfgString, '~/.foresterrc')
    defaultControlFile          = (cfg.CfgString, 'control.yaml')
    defaultControlUri           = cfg.CfgString
    defaultControlType          = (cfg.CfgString, 'WMS')
    defaultForest               = CfgString
    customAliases               = CfgDict(CfgString)
    defaultWmsBase              = (cfg.CfgString, 'http://wheresmystuff.unx.sas.com')


    def __init__(self, config=None, readConfigFiles=True, ignoreErrors=False):
        super(ForesterConfiguration, self).__init__()
        self._config = config
        self.readConfigFiles = readConfigFiles
        self.ignoreErrors = ignoreErrors
        self._readCfg()
        self._aliases = None

    def getDefaultAliases(self):
        if self._aliases is None:                                  
            self._aliases =  {   'user.name' : None,
                            'user.email': None,
                            'alias.co'  : 'checkout',
                            'alias.ci'  : 'commit',
                            'alias.br'  : 'branch',
                            'alias.st'  : 'status',
                            'alias.last': 'log -1 HEAD',
                            'push.default' : 'simple',
                        }
        else:
            self._aliases.update(self.customAliases)
        return self._aliases


    def _readCfg(self, paths=[]):
        if self.readConfigFiles:
            paths = ['./.foresterrc', '~/.foresterrc', '/etc/build-tools/forester.cfg' ]
        if self._config:
            paths.append(self._config)
        for path in paths:
            if path.startswith('~/') and 'HOME' in os.environ:
                path = os.path.join(os.environ['HOME'], path[2:])
            if os.path.isfile(path):
                self.read(path)

