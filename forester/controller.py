#!/usr/bin/python2.6
#
# Copyright (c) SAS Institute Inc.
#
# All rights reserved.
#

import os
import logging
import urlparse

from forester import gitrepo
from forester.scm import wms
from forester.scm import git
from forester.scm import hg

logger = logging.getLogger(__name__)

class Controller(object):
    _registry = {}
    
    @classmethod
    def register(cls, klass):
        cls._registry[klass.ControllerType] = klass

    @classmethod
    def create(cls, controltype, *args, **kwargs):
        return cls._registry.get(controltype)(*args, **kwargs)

class BaseController(object):

    CONTROLLERS = ('WMS', 'GIT', 'HG', 'LOCAL')

    def __init__(self, base, path, controller=None): 
        self.base = base       
        self.path = path
        self.repos = {} 
        self.controller = None
    
    def _getUri(self):
        '''
        Override
        '''
        return

    uri = property(_getUri)

    def isRemote(self, uri=None):
        if not uri:
            uri = self.path
        remote_repo_prefix = ['http://', 'https://', 'git://', 'ssh://']
        for pre in remote_repo_prefix:
            if uri.startswith(pre):
                return True
        assert os.path.exists(uri)
        return False

    def genDirPath(self, uri, subdir):
        url = urlparse.urlparse(uri)
        repo = os.path.basename(url.path).replace('.git','')
        path = os.path.join(url.netloc, repo)
        if subdir:
            path = os.path.join(subdir, path)
        if path.startswith('~/') and 'HOME' in os.environ:
            path = os.path.join(os.environ['HOME'], path[2:])
        else:
            path = os.path.join(os.getcwd(), path)
        return path

    def reader(self):
        '''
        Override depending on Controller Type
        '''
        pass

    def findrepos(self):
        '''
        find control and read it
        clone all the repos
        '''
        return self.reader()


class WmsController(BaseController):
    ControllerType = 'WMS'

    def __init__(self, base, path, branch=None):
        self.base = base
        self.path = path
        self.branch = branch
        self.reposet = set()
        self.wms = wms.WmsRepository(self.base, self.path, self.branch)

    def _getUri(self):
        return self.wms.getGitUri()

    uri = property(_getUri)

    def reader(self):
        data = self.wms.parseRevisionsFromUri()
        for name, info in data.iteritems():
            repo = gitrepo.GitRepo(name=name)
            repo.update(info)
            self.reposet.add(repo)
        return self.reposet


Controller.register(WmsController)

class GitController(BaseController):

    ControllerType = 'GIT'

    def __init__(self, base, path, branch=None):
        self.base = base
        self.path = path
        self.branch = branch
        self.repos = {}
        self.git = git.GitRepository(self.base, self.path, self.branch)
        self.gitcmds = git.GitCommands()

Controller.register(GitController)

class HgController(BaseController):

    ControllerType = 'HG'

    def __init__(self, base, path, branch=None):
        self.base = base
        self.path = path
        self.branch = branch
        self.repos = {}


Controller.register(HgController)

class LocalController(BaseController):

    ControllerType = 'LOCAL'

    def __init__(self, base, path, branch=None):
        self.base = base
        self.path = path
        self.branch = branch
        self.repos = {} 


    def reader(self, path):
        #FILE IS IN YAML 
        # pick up file
        # parse
        # make dict
        from yaml import load
        control = {}
        try:
            logger.info('Reading control file from %s' % path)
            stream = file(path, 'r')
            control = load(stream)
        except IOError, e:
            raise IOError, e
        return control


Controller.register(LocalController)
