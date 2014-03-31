#!/usr/bin/python2.6
#
#
# Copyright (c) SAS Institute Inc.
#
# All rights reserved.

import urlparse
import logging 
import os


from conary import util as conary_util

from forester import config
from forester.scm import git
from forester import errors


logger = logging.getLogger(__name__)

class BaseUtil(git.GitCommands):
    
    def __init__(self, cachedir=None):
        super(BaseUtil, self).__init__(cachedir)
        self.cachedir = cachedir


class InitialSetup(BaseUtil):

    def __init__(self, name=None, email=None, branch=None, 
                        subdir=None, controltype=None, 
                        cachedir=None, cfgfile=None, test=False,) :
        super(InitialSetup, self).__init__(cachedir)
        self.controltype = controltype
        self.controlFile = None
        self.cachedir = cachedir
        self._cfgfile= cfgfile
        self._cfg = None
        if not self._cfg:
            self.getDefaultConfig()
        if not self.cachedir:
            self.cachedir = self._cfg.defaultCacheDir
        if not self.branch:
            self.branch = self._cfg.defaultBranch
        if not self.controltype:
            self.controltype = self._cfg.defaultControlType
        if not self.controlFile:
            self.controlFile = self._cfg.defaultControlFile

        self.debug = self._cfg.debugMode
        self.test = test
        self.subdir = None
        if not self.subdir:
            self.subdir = self._cfg.defaultSubDir

    def getDefaultConfig(self):
        logger.info('Loading default cfg')
        self._cfg = config.ForesterConfiguration(config=self._cfgfile)


    def initialSetup(self,  name=None,
                            email=None,
                            aliases=None,
                            subdir=None,
                            cfgfile=None,
                            forest=None,
                            branch=None,
                            wms=None,
                            wmsbase=None,
                            wmspath=None,
                    ):



        if name:
            self._cfg.userName = name
        if email:
            self._cfg.userEmail = email
        if aliases:
            self._cfg.useAliases = aliases
        if subdir:
            self._cfg.defaultSubDir = subdir
            conary_util.mkdirChain(self._cfg.defaultSubDir)

        self._cfg.logFile = os.path.join(self._cfg.defaultSubDir, 'forester.log')
        self._cfg.tmpDir = os.path.join(self._cfg.defaultSubDir,'tmp')
        self._cfg.defaultCacheDir = os.path.join(self._cfg.defaultSubDir, 'cachedir')   
        self.cachedir = self._cfg.defaultCacheDir
        conary_util.mkdirChain(self._cfg.defaultCacheDir)
        conary_util.mkdirChain(self._cfg.tmpDir)
 
        if wms:
            self._cfg.defaultControlType = 'WMS'
            self._cfg.defaultControlUri = self._cfg.defaultWmsBase

        if forest:      
            self._cfg.defaultForrest = forest
            forestSectionName = 'forest:%s' % forest
            forestSection = self._cfg.setSection(forestSectionName)
            forestSection.ForestName = forest
            if branch:
                forestSection.ForestBranch = branch
            if wms:
                forestSection.ForestControlType = 'WMS'
            if wmsbase:
                forestSection.ForestControlUri = wmsbase
            if wmspath:
                forestSection.ForestControlPath = wmspath
            forestSection.ForestCacheDir = self._cfg.defaultCacheDir
        
        if not cfgfile:
            cfgfile = self._cfg.defaultConfigFile
        if cfgfile.startswith('~/') and 'HOME' in os.environ:
                cfgfile = os.path.join(os.environ['HOME'], cfgfile[2:])

        if aliases:
            if not self._cfg._aliases: 
                self._cfg._aliases = self._cfg.getDefaultAliases()
            self._cfg._aliases['user.name'] = self._cfg.userName
            self._cfg._aliases['user.email'] = self._cfg.userEmail
            self._cfg.customAliases.update(self._cfg._aliases)            
            self.set_globals(self._cfg._aliases)

        self._cfg.writeToFile(cfgfile)
        
