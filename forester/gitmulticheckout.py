import logging
import os
import urlparse

from forester.scm import git

from conary.conaryclient import cmdline

from conary.lib import util as conary_util


logger = logging.getLogger(__name__)

from collections import namedtuple

class GitMultiCheckout(git.GitCommands):
    def __init__(self, forestName, repos, subdir, cachedir, ask=False, readonly=False, cfg=None, test=False):
        super(GitMultiCheckout, self).__init__(cachedir)
        self.forestName = forestName
        self.repos = repos
        self.subdir = subdir
        self.cachedir = cachedir
        self.ask = ask
        self.readonly = readonly
        self.test = test
        self._cfg = cfg

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

    def manglePath(self, path):
        silo, _, rest = path.partition('/')
        path = "%s/%s/%s" % (silo, self.forestName, rest)
        if self.subdir:
            path = os.path.join(self.subdir, path)
        return path

    def prep(self, path):
        path = self.manglePath(path)
        conary_util.mkdirChain(path)
        return path

    def checkoutMultiple(self, branch, newBranch=False, startPoint=None):
        for repo in self.repos:
            self.checkoutOne(repo, branch, newBranch=newBranch, startPoint=startPoint)

    def checkoutOne(self, repo, branch, newBranch=False, startPoint=None):
        okay = True
        local = self.manglePath(repo.path)
        uri = self.mangleUri(repo.uri)
        if self.test:
            logger.info('List head for %s %s', uri, branch)
            logger.info("%s", self.ls_remote(uri, branch))
            return
        logger.info("%s.%s", self.forestName, repo.name)
        if self.ask:
            okay = cmdline.askYn('continue with checkout? [y/N]', default=False)
        if not okay:
            return
        if newBranch:
            cmd, args, kw = self.branch, (local,), dict(branch=branch, startPoint=startPoint)
        else:
            cmd, args, kw = self.checkout, (local,branch,), dict()
        try:
            cmd(*args, **kw)
        except git.ForesterGitError, e:
            logger.exception("Error: %s", e)

    def main(self, branch, newBranch=False, startPoint=None):
        return self.checkoutMultiple(branch, newBranch=newBranch, startPoint=startPoint)

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

