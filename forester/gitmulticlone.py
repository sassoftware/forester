import logging
import os
import urlparse

from forester.scm import git
from forester import errors

from conary.conaryclient import cmdline

logger = logging.getLogger(__name__)

from collections import namedtuple

class SimpleGitRepo(namedtuple('gitrepo', 'name branch uri path head')):
    __slots__ = ()

class GitMultiClone(git.GitCommands):
    def __init__(self, repos, subdir, cachedir, ask=False, readonly=False, cfg=None, test=False):
        super(GitMultiClone, self).__init__(cachedir)
        self.repos = repos
        self.subdir = subdir
        self.cachedir = cachedir
        self.ask = ask
        self.readonly = readonly
        self.test = test
        self.prepped = False
        self._cfg = cfg

    def mkDirs(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        assert os.path.exists(path)

    def _check_remote_heads(self, test, uri, branch=None):
        heads = self.ls_remote(uri, branch)
        for head, commit in heads.items():
            logger.debug('Testing %s %s against %s' % (head, commit, test))
            if commit == test:
                return True
        return False

    def isReadOnly(self, uri):
        readonly_repo_prefix = ['http://', 'https://', 'git://']
        for pre in readonly_repo_prefix:
            if uri.startswith(pre):
                return True
        return False

    def mangleUri(self, uri):
        if not self.readonly and self.isReadOnly(uri):
            url = urlparse.urlparse(uri)
            netloc = url.netloc
            if url.netloc in self._cfg.gitUserMap:
                netloc = ''.join([self._cfg.gitUserMap.get(url.netloc), '@',  url.netloc])  
            if url.scheme == 'git':
                uri = '/'.join(['ssh:/', netloc, 'git', url.path[1:]])
        return uri

    def prep(self, path):
        if self.subdir:
            path = os.path.join(self.subdir, path)
        self.mkDirs(path)
        return path
        
    def cloneMultiple(self):
        self.mkDirs(self.cachedir)
        for repo in self.repos: 
            okay = True
            branch = repo.branch or 'master'
            local = self.prep(repo.path)
            uri = self.mangleUri(repo.uri)
            print 'List head for %s %s' % (uri, branch)
            if self.test:
                print self.ls_remote(uri, branch)
                continue
            if os.path.exists(os.path.join(local, '.git')):
                if self.ask:
                    okay = cmdline.askYn('Dir exists continue with pull? [y/N]', default=False)
                if okay:
                    print "%s/.git exists can not pull" % local
                    print "Not Supported Yet"
            else:
                if self.ask:
                    okay = cmdline.askYn('continue with clone? [y/N]', default=False)
                if okay:
                    self.clone(uri, branch, local, path=None)
        return

    def main(self):
        return self.cloneMultiple()


if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

