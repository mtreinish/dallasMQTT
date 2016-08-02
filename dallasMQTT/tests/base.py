# Copyright 2016 Matthew Treinish
#
# This file is part of dallasMQTT
#
# dallasMQTT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dallasMQTT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dallasMQTT.  If not, see <http://www.gnu.org/licenses/>.

import os

import fixtures
import testtools


class TestCase(testtools.TestCase):

    true = ('True', 'true', '1', 'yes')

    def setUp(self):
        super(TestCase, self).setUp()
        if os.environ.get('OS_STDOUT_CAPTURE') in self.true:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in self.true:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        if (os.environ.get('OS_LOG_CAPTURE') != 'False' and
            os.environ.get('OS_LOG_CAPTURE') != '0'):
            self.useFixture(fixtures.LoggerFixture(nuke_handlers=False,
                                                   level=None))
