import logging
import os
import urlparse

from forester.scm import git

from conary.conaryclient import cmdline

from conary.lib import util as conary_util


logger = logging.getLogger(__name__)

from collections import namedtuple

class GitMultiCommand(git.GitCommands):
    """
    Utility superclass for all subclasses that run git commands on multiple
    repositories in a forest.
    """
    def __init__(self, forestName, repos, subdir, cachedir,
            ask=False, readonly=False, cfg=None, test=False):
        super(GitMultiCommand, self).__init__(cachedir)
        self.forestName = forestName
        self.repos = repos
        self.subdir = subdir
        self.ask = ask
        self.readonly = readonly
        self._cfg = cfg
        self.test = test
        self.error_repos = []

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

    def setup(self):
        """
        Run once at the beginning of commandMultiple.  Subclasses can use this
        to perform per-forest setup.
        """
        pass

    def commandOne(self, repo, *args, **kwargs):
        """
        Run once for each repo in the forest.  Subclasses are responsible for
        argument unpacking.
        """
        pass

    def commandMultiple(self, *args, **kwargs):
        self.setup()
        for repo in self.repos:
            if not self.test:
                if self.shouldRun(repo):
                    self.commandOne(repo, *args, **kwargs)
                else:
                    logger.info('Skipping %s' % repo.name)
            else:
                self.testOne(repo, *args, **kwargs)
        if self.error_repos:
            errors = [ repo.name for repo in self.error_repos ]
            logger.error('Errors in these repositories:\n\t%s\n' % '\n\t'.join(errors))

    def testOne(self, repo, *args, **kwargs):
        uri = self.mangleUri(repo.uri)
        logger.info('List head for %s', uri)
        logger.info("%s", self.ls_remote(uri))

    def shouldRun(self, repo):
        logger.info("%s.%s", self.forestName, repo.name)
        okay = True
        if self.ask:
            okay = cmdline.askYn('continue? [y/N]', default=False)

        return okay

class GitMultiPush(GitMultiCommand):
    def __init__(self, forestName, repos, subdir, cachedir, **kwargs):
        super(GitMultiPush, self).__init__(
                forestName, repos, subdir, cachedir, **kwargs
                )

    def commandOne(self, repo, *args, **kwargs):
        local = self.manglePath(repo.path)
        remote = args[0]
        refspec = args[1]
        cmd, args, kw = self.push, (local, remote, refspec), dict(kwargs)

        try:
            cmd(*args, **kw)
        except git.ForesterGitError, e:
            self.error_repos.append(repo)
            logger.exception("Error: %s", e)

class GitMultiCheckout(GitMultiCommand):
    def __init__(self, forestName, repos, subdir, cachedir, **kwargs):
        super(GitMultiCheckout, self).__init__(
                forestName, repos, subdir, cachedir, **kwargs
                )

    def commandOne(self, repo, *args, **kwargs):
        local = self.manglePath(repo.path)
        branch = args[0]
        newBranch = kwargs.pop('newBranch')

        if newBranch:
            cmd, args, kw = self.branch, (local,), dict(kwargs, branch=branch)
        else:
            cmd, args, kw = self.checkout, (local,branch,), dict()
        try:
            cmd(*args, **kw)
        except git.ForesterGitError, e:
            self.error_repos.append(repo)
            logger.exception("Error: %s", e)

class GitMultiClone(GitMultiCommand):
    def __init__(self, forestName, repos, subdir, cachedir, **kwargs):
        super(GitMultiClone, self).__init__(
                forestName, repos, subdir, cachedir, **kwargs
                )
        self.prepped = False

    def prep(self, path):
        path = self.manglePath(path)
        conary_util.mkdirChain(path)
        return path

    def setup(self):
        conary_util.mkdirChain(self.cachedir)

    def shouldRun(self, repo):
        logger.info("%s.%s", self.forestName, repo.name)

        local = self.prep(repo.path)
        okay = True

        if os.path.exists(os.path.join(local, '.git')):
            if self.ask:
                okay = cmdline.askYn('Dir exists; continue with pull? [y/N]', default=False)
        else:
            if self.ask:
                okay = cmdline.askYn('continue with clone? [y/N]', default=False)

        return okay

    def commandOne(self, repo, *args, **kwargs):
        otherBranch = kwargs.pop('otherBranch', None)
        withPull = kwargs.pop('withPull', False)
        withPush = kwargs.pop('withPush', False)

        if withPush:
            assert otherBranch is not None
        branch = repo.branch or 'master'
        local = self.manglePath(repo.path)
        uri = self.mangleUri(repo.uri)

        if os.path.exists(os.path.join(local, '.git')):
            # First, refresh the origin branch
            cmd, args, kw = self.pull, (local, branch), dict()
        else:
            cmd, args, kw = self.clone, (uri, branch, local), dict(path=None)

        try:
            cmd(*args, **kw)
            if withPull:
                # If merging, pull from the other branch, with pushing if
                # possible
                self.pull(local, otherBranch, withPush=withPush)
        except git.ForesterGitError, e:
            self.error_repos.append(repo)
            if 'Not possible to fast-forward, aborting.' in e.stderr:
                logger.error("%s.%s: Unable to auto-merge", self.forestName,
                        repo.name)
                return
            logger.exception("Error: %s", e)

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()


