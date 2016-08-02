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


from dallasMQTT import listener
from dallasMQTT.tests import base


class TestWorkerPartition(base.TestCase):

    def test_less_devs_than_workers(self):
        maxworkers = 5
        sensors = [1, 2, 3]
        resp = listener.partition_sensors(sensors, maxworkers)
        self.assertEqual([[1], [2], [3]], resp)

    def test_more_devs_than_workers(self):
        maxworkers = 2
        sensors = [1, 2, 3, 4, 5]
        resp = listener.partition_sensors(sensors, maxworkers)
        self.assertEqual([[1, 2], [3, 4], [5]], resp)

    def test_equal_devs_to_workers(self):
        maxworkers = 3
        sensors = [1, 2, 3]
        resp = listener.partition_sensors(sensors, maxworkers)
        self.assertEqual([[1], [2], [3]], resp)
