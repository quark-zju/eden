# hiddenoverride.py - lightweight hidden-ness override
#
# Copyright 2017 Facebook, Inc.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import contextlib
import errno
import os
import time

from mercurial.node import short
from mercurial import (
    dispatch,
    error,
    extensions,
    lock as lockmod,
    obsolete,
    repoview,
    scmutil,
    util,
    vfs as vfsmod,
)

def uisetup(ui):
    extensions.wrapfunction(repoview, 'pinnedrevs', pinnedrevs)
    extensions.wrapfunction(dispatch, 'runcommand', runcommand)
    extensions.wrapfunction(obsolete, 'createmarkers', createmarkers)
    extensions.wrapfunction(scmutil, 'cleanupnodes', cleanupnodes)

def pinnedrevs(orig, repo):
    revs = orig(repo)
    nodemap = repo.changelog.nodemap
    pinnednodes = set(loadpinnednodes(repo))
    tounpin = getattr(repo, '_tounpinnodes', set())
    pinnednodes -= tounpin
    revs.update(nodemap[n] for n in pinnednodes)
    return revs

def loadpinnednodes(repo):
    """yield pinned nodes that are obsoleted and should be visible"""
    if repo is None or not repo.local():
        return
    # the "pinned nodes" file name is "obsinhibit" for compatibility reason
    content = repo.svfs.tryread('obsinhibit') or ''
    unfi = repo.unfiltered()
    nodemap = unfi.changelog.nodemap
    offset = 0
    result = []
    while True:
        node = content[offset:offset + 20]
        if not node:
            break
        if node in nodemap:
            result.append(node)
        offset += 20
    return result

def shouldpinnodes(repo):
    """get nodes that should be pinned: working parent + bookmarks for now"""
    result = set()
    if repo and repo.local():
        # working copy parent
        try:
            wnode = repo.vfs('dirstate').read(20)
            result.add(wnode)
        except Exception:
            pass
        # bookmarks
        result.update(repo.unfiltered()._bookmarks.values())
    return result

@contextlib.contextmanager
def flock(lockpath, description, timeout=-1):
    """A flock based lock object. Currently it is always non-blocking.

    Note that since it is flock based, you can accidentally take it multiple
    times within one process and the first one to be released will release all
    of them. So the caller needs to be careful to not create more than one
    instance per lock.
    """

    # best effort lightweight lock
    try:
        import fcntl
        fcntl.flock
    except ImportError:
        # fallback to Mercurial lock
        vfs = vfsmod.vfs(os.path.dirname(lockpath))
        with lockmod.lock(vfs, os.path.basename(lockpath), timeout=timeout):
            yield
        return
    # make sure lock file exists
    util.makedirs(os.path.dirname(lockpath))
    with open(lockpath, 'a'):
        pass
    lockfd = os.open(lockpath, os.O_RDONLY, 0o664)
    start = time.time()
    while True:
        try:
            fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError as ex:
            if ex.errno == errno.EAGAIN:
                if timeout != -1 and time.time() - start > timeout:
                    raise error.LockHeld(errno.EAGAIN, lockpath, description,
                                         '')
                else:
                    time.sleep(0.05)
                    continue
            raise

    try:
        yield
    finally:
        fcntl.flock(lockfd, fcntl.LOCK_UN)
        os.close(lockfd)

def savepinnednodes(repo, newpin, newunpin, fullargs):
    # take a narrowed lock so it does not affect repo lock
    with flock(repo.svfs.join('obsinhibit.lock'), 'save pinned nodes'):
        orignodes = loadpinnednodes(repo)
        nodes = set(orignodes)
        nodes |= set(newpin)
        nodes -= set(newunpin)
        with util.atomictempfile(repo.svfs.join('obsinhibit')) as f:
            f.write(''.join(nodes))

        desc = lambda s: [short(n) for n in s]
        repo.ui.log('pinnednodes', 'pinnednodes: %r newpin=%r newunpin=%r '
                    'before=%r after=%r\n', fullargs, desc(newpin),
                    desc(newunpin), desc(orignodes), desc(nodes))

def runcommand(orig, lui, repo, cmd, fullargs, *args):
    # return directly for non-repo command
    if not repo:
        return orig(lui, repo, cmd, fullargs, *args)

    shouldpinbefore = shouldpinnodes(repo) | set(loadpinnednodes(repo))
    result = orig(lui, repo, cmd, fullargs, *args)
    # after a command completes, make sure working copy parent and all
    # bookmarks get "pinned".
    newpin = shouldpinnodes(repo) - shouldpinbefore
    newunpin = getattr(repo.unfiltered(), '_tounpinnodes', set())
    # filter newpin by obsolte - ex. if newpin is on a non-obsoleted commit,
    # ignore it.
    if newpin:
        unfi = repo.unfiltered()
        obsoleted = unfi.revs('obsolete()')
        nodemap = unfi.changelog.nodemap
        newpin = set(n for n in newpin
                     if n in nodemap and nodemap[n] in obsoleted)
    # only do a write if something has changed
    if newpin or newunpin:
        savepinnednodes(repo, newpin, newunpin, fullargs)
    return result

def createmarkers(orig, repo, rels, *args, **kwargs):
    # this is a way to unpin revs - precursors are unpinned
    # note: hg debugobsolete does not call this function
    unfi = repo.unfiltered()
    tounpin = getattr(unfi, '_tounpinnodes', set())
    for r in rels:
        try:
            tounpin.add(r[0].node())
        except error.RepoLookupError:
            pass
    unfi._tounpinnodes = tounpin
    return orig(repo, rels, *args, **kwargs)

def cleanupnodes(orig, repo, mapping, *args, **kwargs):
    # this catches cases where cleanupnodes is called but createmarkers is not
    # called. unpin nodes from mapping
    unfi = repo.unfiltered()
    tounpin = getattr(unfi, '_tounpinnodes', set())
    tounpin.update(mapping)
    unfi._tounpinnodes = tounpin
    return orig(repo, mapping, *args, **kwargs)
