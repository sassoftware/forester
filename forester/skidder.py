import logging

from forester import config
from forester import controller
from forester import gitmulticlone

logger = logging.getLogger(__name__)

class Skidder(object):

    def __init__(self, forest, cfgfile=None, base=None, path=None,
                                branch=None, excludes=[], ask=False, 
                                readonly=False, test=False):

        self.section= 'forest:%s' % forest
        self.cfgfile = cfgfile
        self.base = base
        self.path = path
        self.branch = branch
        self.controltype = None
        self._cfg = None
        self.excludes = excludes
        self.ask = ask
        self.readonly = readonly
        self.test = test
        self.getDefaultConfig()
        self.cfgs = {}
        for sectionName in self._cfg.iterSectionNames():
            if self.section in sectionName:
                self.cfgs.setdefault(sectionName, self._cfg.getSection(sectionName))
        self.forestCfg = self.cfgs.get(self.section)
        if not self.branch:
            self.branch = self.forestCfg.ForestBranch
        if not self.base:
            self.base = self.forestCfg.ForestControlUri
        if not self.path:
            self.path = self.forestCfg.ForestControlPath
        if not self.controltype:
            self.controltype = self.forestCfg.ForestControlType
        if not self.test:
            self.test = self.forestCfg.ForestTest
        
        self.subdir = self.forestCfg.ForestSubDir
        self.cachedir = self.forestCfg.ForestCacheDir
        self.excludes = self.excludes + self.forestCfg.ForestExcludes

        if not self.subdir:
            self.subdir = self._cfg.defaultSubDir
        if not self.cachedir:
            self.cachedir = self._cfg.defaultCacheDir
        if not self.branch:
            self.branch = self._cfg.defaultBranch
        if not self.base:
            self.base = self._cfg.defaultControlUri
        if not self.controltype:
            self.controltype = self._cfg.defaultControlType

        assert self.controltype
        assert self.base
        assert self.path

        self.controller = controller.Controller.create(self.controltype,
                                                self.base, 
                                                self.path, 
                                                self.branch, 
                                                )

    def getDefaultConfig(self, cfgFile=None):
        logger.info('Loading default cfg')
        if not cfgFile:
            cfgFile = self.cfgfile
        self._cfg = config.ForesterConfiguration(config=cfgFile)

    def findrepos(self):   
        repos = self.controller.findrepos()
        if 'ERROR' in repos:
            raise 
        return repos

    def main(self):
        reposet = self.findrepos()
        toRemove = set()
        for repo in reposet:
            if repo.name in self.excludes:
                toRemove.add(repo)
                print 'Excluding %s' % repo.name
        reposet.difference_update(toRemove)

        _f = gitmulticlone.GitMultiClone(repos = reposet, 
                                    subdir = self.subdir,
                                    cachedir = self.cachedir, 
                                    ask=self.ask,
                                    readonly = self.readonly,
                                    test = self.test,
                                    )

        _f.main()
