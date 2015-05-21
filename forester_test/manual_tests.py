#!/usr/bin/python

import sys


def usage(argv):
    print 'Usage:'
    print '%s <git uri> <git branch>' % argv[0]
    sys.exit(0)

def testSimpleGitRepo(name, branch, uri, path, head):
    import gitmulticlone
    repo = gitmulticlone.SimpleGitRepo(name, branch, uri, path, head)
    return repo

def testGitMultiClone(repos, subdir, cachedir, ask=True, test=True):
    import gitmulticlone
    forestName = 'aaa'
    _p = gitmulticlone.GitMultiClone(forestName, repos, subdir, cachedir,
                                                ask=ask, test=test)
    _p.main()

def testSkidder(forest, cfgfile=None, base=None, path=None, branch=None, 
                    ask=False, test=False):
    import skidder
    _f = skidder.Skidder(forest, cfgfile=cfgfile, base=base, 
                            path=path, branch=branch, ask=ask, test=test)
    _f.main()

def testWms(base, path, branch=None):
    from forester.scm import wms
    _wms = wms.WmsRepository(base,path,branch=branch)
    stuff = _wms.parseRevisionsFromUri()
    print stuff

    import epdb;epdb.st()

def testWmsController(base, path, branch=None):
    import controller
    _c = controller.WmsController(base,path,branch=branch)

    repos = _c.findrepos()
    print repos
    print _c.uri
    import epdb;epdb.st()

def testController(controltype, base, path, branch=None):
    import controller
    _c = controller.Controller.create(controltype, 
                                base,path,branch=branch)

    repos = _c.findrepos()
    print repos
    print _c.uri
    import epdb;epdb.st()


def testInitial(name, email, aliases, subdir, cfgfile, 
                        forest, branch, wms, wmsbase, wmspath):
    import utils

    iSetup = utils.InitialSetup()

    iSetup.initialSetup(
                name, 
                email,
                aliases,
                subdir,
                cfgfile,
                forest,
                branch,
                wms,
                wmsbase,
                wmspath,
                )



if __name__ == '__main__':
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    uri = None 
    branch = None
    cfgfile = None
    if len(sys.argv) < 2:
        usage(sys.argv)
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    if len(sys.argv) > 2:
        branch = sys.argv[2]
    subdir = 'git'
    name = "Brett Smith"
    email = "bc.smith@sas.com"
    cfgfile = '~/.foresterrc'
    controlfile = 'control.yaml'
    cachedir = 'cachedir'
    controltype = 'WMS'
    aliases = True
    test = True
    excludes = ['barnacle']
    forest = 'appengine'
    forest = 'vapp'
    wms = True
    ask = False
    wmsBase = 'http://wheresmystuff.unx.sas.com'
    #wmsPath = 'scc/appengine'
    wmsPath = 'gitgrid/VirtualApplications/Infrastructure/utilities.ci.bobplans'
    #testInitial(name, email, aliases, subdir, cfgfile, forest, branch, wms, wmsBase, wmsPath)
    #import urlparse
    #testWmsController(wmsBase, wmsPath, branch)
    #testController(controltype, wmsBase, wmsPath, branch)
    #testControl(controlfile)
    testSkidder(forest)
    #testWms(wmsBase, wmsPath, branch)
    sgr_name = 'utilities.webminmaster'
    sgr_branch = '3'
    sgr_uri = 'ssh://git@gitgrid.unx.sas.com/VirtualApplications/Infrastructure/utilities.webminmaster.git'
    sgr_path = 'gitgrid/VirtualApplications/Infrastructure/utilities.webminmaster'
    sgr_head = 'e21c8611e9dd1d262c3e47955c2505d7b19cdce8'
    sgr_test = testSimpleGitRepo(sgr_name, sgr_branch, sgr_uri, sgr_path, sgr_head)
    repos = set()
    repos.add(sgr_test)
    #testGitMultiClone(repos, subdir, cachedir, test=False)
