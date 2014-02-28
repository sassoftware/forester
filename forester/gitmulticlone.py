import logging
import os

from forester.scm import git
from forester import errors

from conary.conaryclient import cmdline

logger = logging.getLogger(__name__)

from collections import namedtuple

class SimpleGitRepo(namedtuple('gitrepo', 'name branch uri path head')):
    __slots__ = ()


class GitMultiClone(git.GitCommands):
    def __init__(self, repos, subdir, cachedir, ask=False, test=False):
        super(GitMultiClone, self).__init__(cachedir)
        self.repos = repos
        self.subdir = subdir
        self.cachedir = cachedir
        self.test = test
        self.ask = ask
        self.prepped = False

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
            print 'List head for %s %s' % (repo.uri, branch)
            if self.test:
                print self.ls_remote(repo.uri, branch)
                continue
            local = self.prep(repo.path)
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
                    self.clone(repo.uri, branch, local, path=None)
        return

    def main(self):
        return self.cloneMultiple()


if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

