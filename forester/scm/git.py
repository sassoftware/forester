#
# Copyright (c) SAS Institute Inc.
#
# All rights reserved.
#

from __future__ import with_statement

'''
Helper functions for dealing with git repositories.
'''

import logging
import os
import subprocess

from .. import scm
from ..errors import ForesterGitError

log = logging.getLogger(__name__)

class GitCommands(object):

    def __init__(self, cachedir=None):
        self.cachedir = cachedir

    def run_git(self, cmd, directory=None):
        if directory:
            log.debug("(cd '%s'; %s)", directory, " ".join(cmd))
        else:
            log.debug("%s", " ".join(cmd))
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
        log.debug
        stdout, stderr = p.communicate()
        if p.returncode:
            raise ForesterGitError(p.returncode, stdout, stderr)
        return stdout

    def ls_remote(self, uri, branch=None):
        cmd = ['git', 'ls-remote', uri]
        if branch:
            cmd.append(branch)
        return self.run_git(cmd)

    def ls_tree(self, branch):
        cmd = ['git', 'ls-tree', '-r', '--name-only', branch]
        return self.run_git(cmd)

    def show_file(self, path):
        uri = '''%s:%s''' % (self.branch, path)
        cmd = ['git', '--no-pager', 'show', uri]
        return self.run_git(cmd)

    def remote_v(self, path):
        cmd = ['git', 'remote', '-v']
        return self.run_git(cmd, path)


    def tags(self, path, msg=None):
        '''
        cd path
        git tag
        git tag -a -m "foo.bar"
        '''
        cmd = ['git', 'tag']
        if msg:cmd = cmd + ['-a', '-m', msg]
        return self.run_git(cmd, path)


    def show(self, path, tag=None):
        '''
        cd path
        git show
        git show <tag>
        ''' 
        cmd = ['git', 'show']
        if tag:cmd.append(tag)
        return self.run_git(cmd, path)

    def set_aliases(self, aliases, gitglobal=False):
        '''
        Where aliases is a dict of attribute and value
        {'alias.co': 'checkout', 'user.name': 'Joe', 
            'user.email': 'j@b.com'}
        '''
        config = ['git', 'config', ]

        if gitglobal:
            config.append('--global')
        else:
            config.extend(['--file', os.path.join(self._cfg.defaultSubDir, '.gitconfig')])
        results = {}
        for attr,value in aliases.iteritems():
            results.setdefault(attr, self.run_git(config + [attr,value]))
        return results

    def set_ignore(self, ignore, gitglobal=False):
        '''
        Where ignore is a list of ignore patterns
        '''
        ignorefile = self._cfg.defaultIgnoreFile
        if ignorefile.startswith('~/') and 'HOME' in os.environ:
            ignorefile = os.path.join(os.environ['HOME'], ignorefile[2:])
        elif gitglobal and 'HOME' in os.environ:
            ignorefile = os.path.join(os.environ['HOME'], ignorefile)
        else:
            ignorefile = os.path.join(self._cfg.defaultSubDir, ignorefile)

        with open(ignorefile, 'a') as f:
            for value in ignore:
                f.write('{0}\n'.format(value))
        return

    def checkout(self, path, branch):
        '''
        cd path
        git checkout <branch>
        '''
        cmd = ['git', 'checkout', branch]
        return self.run_git(cmd, path)

    def branch(self, path, branch=None, startPoint=None):
        '''
        cd path
        if branch is None
        gir branch
        else
        git branch <branch> [startPoint]
        '''
        cmd = ['git', 'branch']
        if branch:
            cmd.extend([branch])
            if startPoint:
                cmd.extend([startPoint])
        return self.run_git(cmd, path)

    def pull(self, path, branch=None, withPush=False):
        '''
        cd path
        git pull
        '''
        cmd = ['git', 'pull']
        if branch:
            cmd.extend(['--ff-only', 'origin', 'refs/heads/%s' % branch])
        ret = self.run_git(cmd, path)
        if not withPush:
            return ret
        cmd = [ 'git', 'push', 'origin' ]
        return self.run_git(cmd, path)

    def clone(self, uri, branch=None, clonedir=None, path=None):
        '''
        git clone -b <branch> <uri> <dir>
        '''
        cmd = ['git', 'clone']
        if branch:
            cmd.extend(['-b' , branch])
        cmd.append(uri)
        if clonedir:cmd.append(clonedir)
        log.info("%s", " ".join(cmd))
        return self.run_git(cmd, path)


class GitRepository(scm.ScmRepository):

    def __init__(self, cacheDir, uri, branch):
        self.uri = uri
        self.branch = branch

        self.dirPath = self.uri.split('//', 1)[-1]
        self.dirPath = self.dirPath.replace('/', '_')
        self.repoDir = os.path.join(cacheDir, self.dirPath, 'git')

    def isLocal(self):
        return self.uri.startswith('/') or self.uri.startswith('file:')

    def getTip(self):
        self.updateCache()
        p = subprocess.Popen(
            ['git', 'rev-parse', self.branch],
            stdout=subprocess.PIPE,
            cwd=self.repoDir,
            )
        stdout, _ = p.communicate()
        if p.returncode:
            raise RuntimeError("git exited with status %s" % p.returncode)
        rev = stdout.split()[0]
        assert len(rev) == 40
        return rev

    def updateCache(self):
        # Create the cache repo if needed.
        if not os.path.isdir(self.repoDir):
            os.makedirs(self.repoDir)
        if not (os.path.isdir(self.repoDir + '/refs')
                or os.path.isdir(self.repoDir + '/.git/refs')):
            subprocess.check_call(
                ['git', 'init', '-q', '--bare'],
                cwd=self.repoDir,
                )
        subprocess.check_call(
            ['git', 'fetch', '-q', self.uri, '+%s:%s' % (
                    self.branch, self.branch)],
            cwd=self.repoDir,
            )

    def checkout(self, workDir):
        p1 = subprocess.Popen(
            ['git', 'archive', '--format=tar', self.branch],
            stdout=subprocess.PIPE,
            cwd=self.repoDir,
            )
        p2 = subprocess.Popen(['tar', '-x'], stdin=p1.stdout, cwd=workDir)
        p1.stdout.close()  # remove ourselves from between git and tar
        p1.wait()
        p2.wait()
        if p1.returncode:
            raise RuntimeError("git exited with status %s" % p1.returncode)
        if p2.returncode:
            raise RuntimeError("tar exited with status %s" % p1.returncode)

    def run_git(self, cmd):
        directory = None
        if os.path.exists(self.repoDir):
            directory = self.repoDir
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, cwd=directory)
        stdout, _ = p.communicate()
        if p.returncode:
            raise RuntimeError("git exited with status %s" % p.returncode)
        return stdout

    def ls_remote(self, uri, branch=None):
        cmd = ['git', 'ls-remote', uri]
        if branch:
            cmd.append(branch)
        stdout = self.run_git(cmd)
        heads = {}
        for head in stdout.splitlines():
            sha, name = head.split('\t')
            assert sha and name
            heads[name] = sha
        return heads

    def ls_tree(self, branch):
        cmd = ['git', 'ls-tree', '-r', '--name-only', branch]
        stdout = self.run_git(cmd)
        files = {}
        files[branch] = [x for x in stdout.splitlines() if x]
        return files

    def show_file(self, path):
        uri = '''%s:%s''' % (self.branch, path)
        cmd = ['git', '--no-pager', 'show', uri]
        return self.run_git(cmd)

    def getAction(self, extra=''):
        return 'addGitSnapshot(%r, branch=%r, tag=%r%s)' % (
                self.uri, self.branch, self.revision, extra)
