import logging
import os
import urlparse

from forester.scm import git

from conary.conaryclient import cmdline

from conary.lib import util as conary_util


logger = logging.getLogger(__name__)

from collections import namedtuple

class SimpleGitRepo(namedtuple('gitrepo', 'name branch uri path head')):
    __slots__ = ()

class GitMultiClone(git.GitCommands):
    def __init__(self, forestName, repos, subdir, cachedir, ask=False, readonly=False, cfg=None, test=False):
        super(GitMultiClone, self).__init__(cachedir)
        self.forestName = forestName
        self.repos = repos
        self.subdir = subdir
        self.cachedir = cachedir
        self.ask = ask
        self.readonly = readonly
        self.test = test
        self.prepped = False
        self._cfg = cfg

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
        silo, _, rest = path.partition('/')
        path = "%s/%s/%s" % (silo, self.forestName, rest)
        if self.subdir:
            path = os.path.join(self.subdir, path)
        conary_util.mkdirChain(path)
        return path

    def cloneMultiple(self, otherBranch, withPull=False, withPush=False):
        conary_util.mkdirChain(self.cachedir)
        for repo in self.repos:
            self.cloneOne(repo, otherBranch=otherBranch, withPull=withPull,
                    withPush=withPush)

    def cloneOne(self, repo, otherBranch=None, withPull=False, withPush=False):
        if withPush:
            assert otherBranch is not None
        okay = True
        branch = repo.branch or 'master'
        local = self.prep(repo.path)
        uri = self.mangleUri(repo.uri)
        if self.test:
            logger.info('List head for %s %s', uri, branch)
            logger.info("%s", self.ls_remote(uri, branch))
            return
        logger.info("%s.%s", self.forestName, repo.name)
        if os.path.exists(os.path.join(local, '.git')):
            if self.ask:
                okay = cmdline.askYn('Dir exists; continue with pull? [y/N]', default=False)
            if not okay:
                return
            # First, refresh the origin branch
            cmd, args, kw = self.pull, (local, branch), dict()
        else:
            if self.ask:
                okay = cmdline.askYn('continue with clone? [y/N]', default=False)
            if not okay:
                return
            cmd, args, kw = self.clone, (uri, branch, local), dict(path=None)
        try:
            cmd(*args, **kw)
            if withPull:
                # If merging, pull from the other branch, with pushing if
                # possible
                self.pull(local, otherBranch, withPush=withPush)
        except git.ForesterGitError, e:
            if 'Not possible to fast-forward, aborting.' in e.stderr:
                logger.error("%s.%s: Unable to auto-merge", self.forestName,
                        repo.name)
                return
            logger.exception("Error: %s", e)

    def main(self, otherBranch, withPull=False, withPush=False):
        return self.cloneMultiple(otherBranch, withPull=withPull,
                withPush=withPush)

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

