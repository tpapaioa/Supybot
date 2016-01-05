###
# Copyright (c) 2002-2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

from supybot.test import *

import os
import unittest

import supybot.conf as conf
import supybot.world as world
import supybot.ircdb as ircdb
import supybot.ircutils as ircutils

class IrcdbTestCase(SupyTestCase):
    def setUp(self):
        world.testing = False
        SupyTestCase.setUp(self)

    def tearDown(self):
        world.testing = True
        SupyTestCase.tearDown(self)

class FunctionsTestCase(IrcdbTestCase):
    def testIsAntiCapability(self):
        self.assertFalse(ircdb.isAntiCapability('foo'))
        self.assertFalse(ircdb.isAntiCapability('#foo,bar'))
        self.assertTrue(ircdb.isAntiCapability('-foo'))
        self.assertTrue(ircdb.isAntiCapability('#foo,-bar'))
        self.assertTrue(ircdb.isAntiCapability('#foo.bar,-baz'))

    def testIsChannelCapability(self):
        self.assertFalse(ircdb.isChannelCapability('foo'))
        self.assertTrue(ircdb.isChannelCapability('#foo,bar'))
        self.assertTrue(ircdb.isChannelCapability('#foo.bar,baz'))
        self.assertTrue(ircdb.isChannelCapability('#foo,bar.baz'))

    def testMakeAntiCapability(self):
        self.assertEqual(ircdb.makeAntiCapability('foo'), '-foo')
        self.assertEqual(ircdb.makeAntiCapability('#foo,bar'), '#foo,-bar')

    def testMakeChannelCapability(self):
        self.assertEqual(ircdb.makeChannelCapability('#f', 'b'), '#f,b')
        self.assertEqual(ircdb.makeChannelCapability('#f', '-b'), '#f,-b')

    def testFromChannelCapability(self):
        self.assertEqual(ircdb.fromChannelCapability('#foo,bar'),
                         ['#foo', 'bar'])
        self.assertEqual(ircdb.fromChannelCapability('#foo.bar,baz'),
                         ['#foo.bar', 'baz'])
        self.assertEqual(ircdb.fromChannelCapability('#foo,bar.baz'),
                         ['#foo', 'bar.baz'])

    def testUnAntiCapability(self):
        self.assertEqual(ircdb.unAntiCapability('-bar'), 'bar')
        self.assertEqual(ircdb.unAntiCapability('#foo,-bar'), '#foo,bar')
        self.assertEqual(ircdb.unAntiCapability('#foo.bar,-baz'),
                         '#foo.bar,baz')

    def testInvertCapability(self):
        self.assertEqual(ircdb.invertCapability('bar'), '-bar')
        self.assertEqual(ircdb.invertCapability('-bar'), 'bar')
        self.assertEqual(ircdb.invertCapability('#foo,bar'), '#foo,-bar')
        self.assertEqual(ircdb.invertCapability('#foo,-bar'), '#foo,bar')


class CapabilitySetTestCase(SupyTestCase):
    def testGeneral(self):
        d = ircdb.CapabilitySet()
        self.assertRaises(KeyError, d.check, 'foo')
        d = ircdb.CapabilitySet(('foo',))
        self.assertTrue(d.check('foo'))
        self.assertFalse(d.check('-foo'))
        d.add('bar')
        self.assertTrue(d.check('bar'))
        self.assertFalse(d.check('-bar'))
        d.add('-baz')
        self.assertFalse(d.check('baz'))
        self.assertTrue(d.check('-baz'))
        d.add('-bar')
        self.assertFalse(d.check('bar'))
        self.assertTrue(d.check('-bar'))
        d.remove('-bar')
        self.assertRaises(KeyError, d.check, '-bar')
        self.assertRaises(KeyError, d.check, 'bar')

    def testReprEval(self):
        s = ircdb.UserCapabilitySet()
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))
        s.add('foo')
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))
        s.add('bar')
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))

    def testContains(self):
        s = ircdb.CapabilitySet()
        self.assertFalse('foo' in s)
        self.assertFalse('-foo' in s)
        s.add('foo')
        self.assertTrue('foo' in s)
        self.assertTrue('-foo' in s)
        s.remove('foo')
        self.assertFalse('foo' in s)
        self.assertFalse('-foo' in s)
        s.add('-foo')
        self.assertTrue('foo' in s)
        self.assertTrue('-foo' in s)

    def testCheck(self):
        s = ircdb.CapabilitySet()
        self.assertRaises(KeyError, s.check, 'foo')
        self.assertRaises(KeyError, s.check, '-foo')
        s.add('foo')
        self.assertTrue(s.check('foo'))
        self.assertFalse(s.check('-foo'))
        s.remove('foo')
        self.assertRaises(KeyError, s.check, 'foo')
        self.assertRaises(KeyError, s.check, '-foo')
        s.add('-foo')
        self.assertFalse(s.check('foo'))
        self.assertTrue(s.check('-foo'))
        s.remove('-foo')
        self.assertRaises(KeyError, s.check, 'foo')
        self.assertRaises(KeyError, s.check, '-foo')

    def testAdd(self):
        s = ircdb.CapabilitySet()
        s.add('foo')
        s.add('-foo')
        self.assertFalse(s.check('foo'))
        self.assertTrue(s.check('-foo'))
        s.add('foo')
        self.assertTrue(s.check('foo'))
        self.assertFalse(s.check('-foo'))


class UserCapabilitySetTestCase(SupyTestCase):
    def testOwnerHasAll(self):
        d = ircdb.UserCapabilitySet(('owner',))
        self.assertFalse(d.check('-foo'))
        self.assertTrue(d.check('foo'))

    def testOwnerIsAlwaysPresent(self):
        d = ircdb.UserCapabilitySet()
        self.assertTrue('owner' in d)
        self.assertTrue('-owner' in d)
        self.assertFalse(d.check('owner'))
        d.add('owner')
        self.assertTrue(d.check('owner'))

    def testReprEval(self):
        s = ircdb.UserCapabilitySet()
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))
        s.add('foo')
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))
        s.add('bar')
        self.assertEqual(s, eval(repr(s), ircdb.__dict__, ircdb.__dict__))

    def testOwner(self):
        s = ircdb.UserCapabilitySet()
        s.add('owner')
        self.assertTrue('foo' in s)
        self.assertTrue('-foo' in s)
        self.assertTrue(s.check('owner'))
        self.assertFalse(s.check('-owner'))
        self.assertFalse(s.check('-foo'))
        self.assertTrue(s.check('foo'))

##     def testWorksAfterReload(self):
##         s = ircdb.UserCapabilitySet(['owner'])
##         self.failUnless(s.check('owner'))
##         import sets
##         reload(sets)
##         self.failUnless(s.check('owner'))


class IrcUserTestCase(IrcdbTestCase):
    def testCapabilities(self):
        u = ircdb.IrcUser()
        u.addCapability('foo')
        self.assertTrue(u._checkCapability('foo'))
        self.assertFalse(u._checkCapability('-foo'))
        u.addCapability('-bar')
        self.assertTrue(u._checkCapability('-bar'))
        self.assertFalse(u._checkCapability('bar'))
        u.removeCapability('foo')
        u.removeCapability('-bar')
        self.assertRaises(KeyError, u._checkCapability, 'foo')
        self.assertRaises(KeyError, u._checkCapability, '-bar')

    def testAddhostmask(self):
        u = ircdb.IrcUser()
        self.assertRaises(ValueError, u.addHostmask, '*!*@*')

    def testRemoveHostmask(self):
        u = ircdb.IrcUser()
        u.addHostmask('foo!bar@baz')
        self.assertTrue(u.checkHostmask('foo!bar@baz'))
        u.addHostmask('foo!bar@baz')
        u.removeHostmask('foo!bar@baz')
        self.assertFalse(u.checkHostmask('foo!bar@baz'))

    def testOwner(self):
        u = ircdb.IrcUser()
        u.addCapability('owner')
        self.assertTrue(u._checkCapability('foo'))
        self.assertFalse(u._checkCapability('-foo'))

    def testInitCapabilities(self):
        u = ircdb.IrcUser(capabilities=['foo'])
        self.assertTrue(u._checkCapability('foo'))

    def testPassword(self):
        u = ircdb.IrcUser()
        u.setPassword('foobar')
        self.assertTrue(u.checkPassword('foobar'))
        self.assertFalse(u.checkPassword('somethingelse'))

    def testTimeoutAuth(self):
        orig = conf.supybot.databases.users.timeoutIdentification()
        try:
            conf.supybot.databases.users.timeoutIdentification.setValue(2)
            u = ircdb.IrcUser()
            u.addAuth('foo!bar@baz')
            self.assertTrue(u.checkHostmask('foo!bar@baz'))
            time.sleep(2.1)
            self.assertFalse(u.checkHostmask('foo!bar@baz'))
        finally:
            conf.supybot.databases.users.timeoutIdentification.setValue(orig)

    def testMultipleAuth(self):
        orig = conf.supybot.databases.users.timeoutIdentification()
        try:
            conf.supybot.databases.users.timeoutIdentification.setValue(2)
            u = ircdb.IrcUser()
            u.addAuth('foo!bar@baz')
            self.assertTrue(u.checkHostmask('foo!bar@baz'))
            u.addAuth('foo!bar@baz')
            self.assertTrue(u.checkHostmask('foo!bar@baz'))
            self.assertTrue(len(u.auth) == 1)
            u.addAuth('boo!far@fizz')
            self.assertTrue(u.checkHostmask('boo!far@fizz'))
            time.sleep(2.1)
            self.assertFalse(u.checkHostmask('foo!bar@baz'))
            self.assertFalse(u.checkHostmask('boo!far@fizz'))
        finally:
            conf.supybot.databases.users.timeoutIdentification.setValue(orig)

    def testHashedPassword(self):
        u = ircdb.IrcUser()
        u.setPassword('foobar', hashed=True)
        self.assertTrue(u.checkPassword('foobar'))
        self.assertFalse(u.checkPassword('somethingelse'))
        self.assertNotEqual(u.password, 'foobar')

    def testHostmasks(self):
        prefix = 'foo12341234!bar@baz.domain.tld'
        hostmasks = ['*!bar@baz.domain.tld', 'foo12341234!*@*']
        u = ircdb.IrcUser()
        self.assertFalse(u.checkHostmask(prefix))
        for hostmask in hostmasks:
            u.addHostmask(hostmask)
        self.assertTrue(u.checkHostmask(prefix))

    def testAuth(self):
        prefix = 'foo!bar@baz'
        u = ircdb.IrcUser()
        u.addAuth(prefix)
        self.assertTrue(u.auth)
        u.clearAuth()
        self.assertFalse(u.auth)

    def testIgnore(self):
        u = ircdb.IrcUser(ignore=True)
        self.assertFalse(u._checkCapability('foo'))
        self.assertTrue(u._checkCapability('-foo'))

    def testRemoveCapability(self):
        u = ircdb.IrcUser(capabilities=('foo',))
        self.assertRaises(KeyError, u.removeCapability, 'bar')

class IrcChannelTestCase(IrcdbTestCase):
    def testInit(self):
        c = ircdb.IrcChannel()
        self.assertFalse(c._checkCapability('op'))
        self.assertFalse(c._checkCapability('voice'))
        self.assertFalse(c._checkCapability('halfop'))
        self.assertFalse(c._checkCapability('protected'))

    def testCapabilities(self):
        c = ircdb.IrcChannel(defaultAllow=False)
        self.assertFalse(c._checkCapability('foo'))
        c.addCapability('foo')
        self.assertTrue(c._checkCapability('foo'))
        c.removeCapability('foo')
        self.assertFalse(c._checkCapability('foo'))

    def testDefaultCapability(self):
        c = ircdb.IrcChannel()
        c.setDefaultCapability(False)
        self.assertFalse(c._checkCapability('foo'))
        self.assertTrue(c._checkCapability('-foo'))
        c.setDefaultCapability(True)
        self.assertTrue(c._checkCapability('foo'))
        self.assertFalse(c._checkCapability('-foo'))

    def testLobotomized(self):
        c = ircdb.IrcChannel(lobotomized=True)
        self.assertTrue(c.checkIgnored('foo!bar@baz'))

    def testIgnored(self):
        prefix = 'foo!bar@baz'
        banmask = ircutils.banmask(prefix)
        c = ircdb.IrcChannel()
        self.assertFalse(c.checkIgnored(prefix))
        c.addIgnore(banmask)
        self.assertTrue(c.checkIgnored(prefix))
        c.removeIgnore(banmask)
        self.assertFalse(c.checkIgnored(prefix))
        c.addBan(banmask)
        self.assertTrue(c.checkIgnored(prefix))
        c.removeBan(banmask)
        self.assertFalse(c.checkIgnored(prefix))

class UsersDictionaryTestCase(IrcdbTestCase):
    filename = os.path.join(conf.supybot.directories.conf(),
                            'UsersDictionaryTestCase.conf')
    def setUp(self):
        try:
            os.remove(self.filename)
        except:
            pass
        self.users = ircdb.UsersDictionary()
        IrcdbTestCase.setUp(self)

    def testIterAndNumUsers(self):
        self.assertEqual(self.users.numUsers(), 0)
        u = self.users.newUser()
        hostmask = 'foo!xyzzy@baz.domain.com'
        banmask = ircutils.banmask(hostmask)
        u.addHostmask(banmask)
        u.name = 'foo'
        self.users.setUser(u)
        self.assertEqual(self.users.numUsers(), 1)
        u = self.users.newUser()
        hostmask = 'biff!fladksfj@blakjdsf'
        banmask = ircutils.banmask(hostmask)
        u.addHostmask(banmask)
        u.name = 'biff'
        self.users.setUser(u)
        self.assertEqual(self.users.numUsers(), 2)
        self.users.delUser(2)
        self.assertEqual(self.users.numUsers(), 1)
        self.users.delUser(1)
        self.assertEqual(self.users.numUsers(), 0)

    def testGetSetDelUser(self):
        self.assertRaises(KeyError, self.users.getUser, 'foo')
        self.assertRaises(KeyError,
                          self.users.getUser, 'foo!xyzzy@baz.domain.com')
        u = self.users.newUser()
        hostmask = 'foo!xyzzy@baz.domain.com'
        banmask = ircutils.banmask(hostmask)
        u.addHostmask(banmask)
        u.addHostmask(hostmask)
        u.name = 'foo'
        self.users.setUser(u)
        self.assertEqual(self.users.getUser('foo'), u)
        self.assertEqual(self.users.getUser('FOO'), u)
        self.assertEqual(self.users.getUser(hostmask), u)
        self.assertEqual(self.users.getUser(banmask), u)
        # The UsersDictionary shouldn't allow users to be added whose hostmasks
        # match another user's already in the database.
        u2 = self.users.newUser()
        u2.addHostmask('*!xyzzy@baz.domain.c?m')
        self.assertRaises(ValueError, self.users.setUser, u2)


class CheckCapabilityTestCase(IrcdbTestCase):
    filename = os.path.join(conf.supybot.directories.conf(),
                            'CheckCapabilityTestCase.conf')
    owner = 'owner!owner@owner'
    nothing = 'nothing!nothing@nothing'
    justfoo = 'justfoo!justfoo@justfoo'
    antifoo = 'antifoo!antifoo@antifoo'
    justchanfoo = 'justchanfoo!justchanfoo@justchanfoo'
    antichanfoo = 'antichanfoo!antichanfoo@antichanfoo'
    securefoo = 'securefoo!securefoo@securefoo'
    channel = '#channel'
    cap = 'foo'
    anticap = ircdb.makeAntiCapability(cap)
    chancap = ircdb.makeChannelCapability(channel, cap)
    antichancap = ircdb.makeAntiCapability(chancap)
    chanop = ircdb.makeChannelCapability(channel, 'op')
    channelnothing = ircdb.IrcChannel()
    channelcap = ircdb.IrcChannel()
    channelcap.addCapability(cap)
    channelanticap = ircdb.IrcChannel()
    channelanticap.addCapability(anticap)
    def setUp(self):
        IrcdbTestCase.setUp(self)
        try:
            os.remove(self.filename)
        except:
            pass
        self.users = ircdb.UsersDictionary()
        #self.users.open(self.filename)
        self.channels = ircdb.ChannelsDictionary()
        #self.channels.open(self.filename)

        owner = self.users.newUser()
        owner.name = 'owner'
        owner.addCapability('owner')
        owner.addHostmask(self.owner)
        self.users.setUser(owner)

        nothing = self.users.newUser()
        nothing.name = 'nothing'
        nothing.addHostmask(self.nothing)
        self.users.setUser(nothing)

        justfoo = self.users.newUser()
        justfoo.name = 'justfoo'
        justfoo.addCapability(self.cap)
        justfoo.addHostmask(self.justfoo)
        self.users.setUser(justfoo)

        antifoo = self.users.newUser()
        antifoo.name = 'antifoo'
        antifoo.addCapability(self.anticap)
        antifoo.addHostmask(self.antifoo)
        self.users.setUser(antifoo)

        justchanfoo = self.users.newUser()
        justchanfoo.name = 'justchanfoo'
        justchanfoo.addCapability(self.chancap)
        justchanfoo.addHostmask(self.justchanfoo)
        self.users.setUser(justchanfoo)

        antichanfoo = self.users.newUser()
        antichanfoo.name = 'antichanfoo'
        antichanfoo.addCapability(self.antichancap)
        antichanfoo.addHostmask(self.antichanfoo)
        self.users.setUser(antichanfoo)

        securefoo = self.users.newUser()
        securefoo.name = 'securefoo'
        securefoo.addCapability(self.cap)
        securefoo.secure = True
        securefoo.addHostmask(self.securefoo)
        self.users.setUser(securefoo)

        channel = ircdb.IrcChannel()
        self.channels.setChannel(self.channel, channel)

    def checkCapability(self, hostmask, capability):
        return ircdb.checkCapability(hostmask, capability,
                                     self.users, self.channels)

    def testOwner(self):
        self.assertTrue(self.checkCapability(self.owner, self.cap))
        self.assertFalse(self.checkCapability(self.owner, self.anticap))
        self.assertTrue(self.checkCapability(self.owner, self.chancap))
        self.assertFalse(self.checkCapability(self.owner, self.antichancap))
        self.channels.setChannel(self.channel, self.channelanticap)
        self.assertTrue(self.checkCapability(self.owner, self.cap))
        self.assertFalse(self.checkCapability(self.owner, self.anticap))

    def testNothingAgainstChannel(self):
        self.channels.setChannel(self.channel, self.channelnothing)
        self.assertEqual(self.checkCapability(self.nothing, self.chancap),
                         self.channelnothing.defaultAllow)
        self.channelnothing.defaultAllow = not self.channelnothing.defaultAllow
        self.channels.setChannel(self.channel, self.channelnothing)
        self.assertEqual(self.checkCapability(self.nothing, self.chancap),
                         self.channelnothing.defaultAllow)
        self.channels.setChannel(self.channel, self.channelcap)
        self.assertTrue(self.checkCapability(self.nothing, self.chancap))
        self.assertFalse(self.checkCapability(self.nothing, self.antichancap))
        self.channels.setChannel(self.channel, self.channelanticap)
        self.assertFalse(self.checkCapability(self.nothing, self.chancap))
        self.assertTrue(self.checkCapability(self.nothing, self.antichancap))

    def testNothing(self):
        self.assertEqual(self.checkCapability(self.nothing, self.cap),
                         conf.supybot.capabilities.default())
        self.assertEqual(self.checkCapability(self.nothing, self.anticap),
                         not conf.supybot.capabilities.default())

    def testJustFoo(self):
        self.assertTrue(self.checkCapability(self.justfoo, self.cap))
        self.assertFalse(self.checkCapability(self.justfoo, self.anticap))

    def testAntiFoo(self):
        self.assertTrue(self.checkCapability(self.antifoo, self.anticap))
        self.assertFalse(self.checkCapability(self.antifoo, self.cap))

    def testJustChanFoo(self):
        self.channels.setChannel(self.channel, self.channelnothing)
        self.assertTrue(self.checkCapability(self.justchanfoo, self.chancap))
        self.assertFalse(self.checkCapability(self.justchanfoo, self.antichancap))
        self.channelnothing.defaultAllow = not self.channelnothing.defaultAllow
        self.assertTrue(self.checkCapability(self.justchanfoo, self.chancap))
        self.assertFalse(self.checkCapability(self.justchanfoo, self.antichancap))
        self.channels.setChannel(self.channel, self.channelanticap)
        self.assertTrue(self.checkCapability(self.justchanfoo, self.chancap))
        self.assertFalse(self.checkCapability(self.justchanfoo, self.antichancap))

    def testChanOpCountsAsEverything(self):
        self.channels.setChannel(self.channel, self.channelanticap)
        id = self.users.getUserId('nothing')
        u = self.users.getUser(id)
        u.addCapability(self.chanop)
        self.users.setUser(u)
        self.assertTrue(self.checkCapability(self.nothing, self.chancap))
        self.channels.setChannel(self.channel, self.channelnothing)
        self.assertTrue(self.checkCapability(self.nothing, self.chancap))
        self.channelnothing.defaultAllow = not self.channelnothing.defaultAllow
        self.assertTrue(self.checkCapability(self.nothing, self.chancap))

    def testAntiChanFoo(self):
        self.channels.setChannel(self.channel, self.channelnothing)
        self.assertFalse(self.checkCapability(self.antichanfoo, self.chancap))
        self.assertTrue(self.checkCapability(self.antichanfoo,
                                             self.antichancap))

    def testSecurefoo(self):
        self.assertTrue(self.checkCapability(self.securefoo, self.cap))
        id = self.users.getUserId(self.securefoo)
        u = self.users.getUser(id)
        u.addAuth(self.securefoo)
        self.users.setUser(u)
        try:
            originalConfDefaultAllow = conf.supybot.capabilities.default()
            conf.supybot.capabilities.default.set('False')
            self.assertFalse(self.checkCapability('a' + self.securefoo, self.cap))
        finally:
            conf.supybot.capabilities.default.set(str(originalConfDefaultAllow))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

