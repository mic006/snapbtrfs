#! /usr/bin/python3

# Copyright 2021 Michel Palleau
#
# This file is part of snapbtrfs.
#
# snapbtrfs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snapbtrfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with snapbtrfs. If not, see <https://www.gnu.org/licenses/>.

"""
Test snapbtrfs methods
"""

import collections
import datetime
import unittest

import snapbtrfs


class DateTimeUtilTest(unittest.TestCase):
    """
    Unit tests for class DateTimeUtil
    """

    def test_round_beginning_hour(self):
        """
        Test DateTimeUtil.round_beginning_hour()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.round_beginning_hour(tst.ts),
                    tst.expected_result,
                )

    def test_round_beginning_day(self):
        """
        Test DateTimeUtil.round_beginning_day()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 25, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 10, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 10, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 8, 26, 14, 2, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 8, 25, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 8, 10, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 8, 10, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 3, 31, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 3, 30, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(
                    2019,
                    10,
                    27,
                    6,
                    12,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 10, 26, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.round_beginning_day(tst.ts),
                    tst.expected_result,
                )

    def test_round_beginning_month(self):
        """
        Test DateTimeUtil.round_beginning_month()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 11, 30, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 11, 30, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 11, 30, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 8, 26, 14, 2, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 7, 31, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 7, 31, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 7, 31, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 3, 31, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 2, 28, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(
                    2019, 3, 3, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 2, 28, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019,
                    10,
                    27,
                    6,
                    12,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 9, 30, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
            TestEntry(
                datetime.datetime(
                    2019, 10, 7, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 9, 30, 22, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.round_beginning_month(tst.ts),
                    tst.expected_result,
                )

    def test_round_beginning_week(self):
        """
        Test DateTimeUtil.round_beginning_week()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 22, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 22, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 22, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 3, 31, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 3, 24, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(
                    2019, 3, 29, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 3, 24, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019,
                    10,
                    27,
                    6,
                    12,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 10, 20, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
            TestEntry(
                datetime.datetime(
                    2019,
                    10,
                    27,
                    0,
                    12,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 10, 20, 22, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.round_beginning_week(tst.ts),
                    tst.expected_result,
                )

    def test_round_beginning_year(self):
        """
        Test DateTimeUtil.round_beginning_year()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 8, 26, 14, 2, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 7, 31, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 3, 31, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(
                    2019, 3, 3, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019,
                    10,
                    27,
                    6,
                    12,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),  # DST fall
            TestEntry(
                datetime.datetime(
                    2019, 10, 7, 6, 12, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.round_beginning_year(tst.ts),
                    tst.expected_result,
                )

    def test_prev_hour(self):
        """
        Test DateTimeUtil.prev_hour()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 13, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 26, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 25, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 25, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 25, 22, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.prev_hour(tst.ts), tst.expected_result
                )

    def test_prev_day(self):
        """
        Test DateTimeUtil.prev_day()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 25, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 10, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 9, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(
                    2019, 8, 26, 14, 2, 42, 123456, tzinfo=datetime.timezone.utc
                ),
                datetime.datetime(2019, 8, 25, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 8, 10, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 8, 9, 22, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 3, 31, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 3, 30, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(2019, 10, 27, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 10, 26, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.prev_day(tst.ts), tst.expected_result
                )

    def test_prev_week(self):
        """
        Test DateTimeUtil.prev_week()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 12, 22, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 22, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 15, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 10, 27, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 10, 20, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
            TestEntry(
                datetime.datetime(2019, 3, 31, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 3, 24, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(2019, 1, 6, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2018, 12, 30, 23, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.prev_week(tst.ts), tst.expected_result
                )

    def test_prev_month(self):
        """
        Test DateTimeUtil.prev_month()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2019, 11, 30, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 11, 30, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 10, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 10, 31, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 9, 30, 22, tzinfo=datetime.timezone.utc),
            ),  # DST fall
            TestEntry(
                datetime.datetime(2019, 3, 31, 22, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 2, 28, 23, tzinfo=datetime.timezone.utc),
            ),  # DST spring
            TestEntry(
                datetime.datetime(2019, 1, 31, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2018, 11, 30, 23, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.prev_month(tst.ts), tst.expected_result
                )

    def test_prev_year(self):
        """
        Test DateTimeUtil.prev_year()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts expected_result")
        tests = (
            TestEntry(
                datetime.datetime(
                    2019,
                    12,
                    26,
                    14,
                    2,
                    42,
                    123456,
                    tzinfo=datetime.timezone.utc,
                ),
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2018, 12, 31, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2017, 12, 31, 23, tzinfo=datetime.timezone.utc),
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                self.assertEqual(
                    snapbtrfs.DateTimeUtil.prev_year(tst.ts), tst.expected_result
                )


class ExistingSnapshotsCollectionTest(unittest.TestCase):
    """
    Unit tests for class ExistingSnapshotsCollection
    """

    def test_find_oldest_in_window(self):
        """
        Test ExistingSnapshotsCollection.find_oldest_in_window()
        """
        existing_snapshots = (
            "2019-12-26 15:02:42 +0100",
            "2019-12-26 13:00:24 +0100",
            "2019-12-24 02:47:42 +0100",
            "2019-12-25 11:03:32 +0100",
            "2019-12-01 07:52:42 +0100",
            "2019-12-26 14:01:17 +0100",
            "2019-11-07 08:02:42 +0100",
        )
        snap_collection = snapbtrfs.ExistingSnapshotsCollection()
        for ts_str in existing_snapshots:
            snap_collection.add(snapbtrfs.ExistingSnapshot(ts_str=ts_str))
        TestEntry = collections.namedtuple("TestEntry", "begin end expected_result")
        tests = (
            TestEntry(
                datetime.datetime(2019, 12, 26, 14, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 15, tzinfo=datetime.timezone.utc),
                datetime.datetime(
                    2019, 12, 26, 14, 2, 42, tzinfo=datetime.timezone.utc
                ),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 26, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 15, tzinfo=datetime.timezone.utc),
                datetime.datetime(
                    2019, 12, 26, 12, 0, 24, tzinfo=datetime.timezone.utc
                ),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 26, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 12, tzinfo=datetime.timezone.utc),
                None,
            ),
            TestEntry(
                datetime.datetime(2019, 12, 1, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 26, 15, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 1, 6, 52, 42, tzinfo=datetime.timezone.utc),
            ),
            TestEntry(
                datetime.datetime(2019, 12, 27, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2019, 12, 28, 0, tzinfo=datetime.timezone.utc),
                None,
            ),
        )
        for tst in tests:
            with self.subTest(tst=tst):
                snap = snap_collection.find_oldest_in_window(tst.begin, tst.end)
                if tst.expected_result is None:
                    self.assertIsNone(snap)
                else:
                    self.assertEqual(snap.ts, tst.expected_result)

    def test_mark_period(self):
        """
        Test ExistingSnapshotsCollection.mark_period()
        """
        TestEntry = collections.namedtuple("TestEntry", "ts_str is_kept")
        existing_snapshots = [
            TestEntry("2019-12-26 15:02:42 +0100", False),
            TestEntry("2019-12-26 14:01:17 +0100", False),
            TestEntry("2019-12-26 13:00:24 +0100", True),
            TestEntry("2019-12-25 11:03:32 +0100", True),
            TestEntry("2019-12-24 17:47:42 +0100", False),
            TestEntry("2019-12-24 04:47:42 +0100", True),
            TestEntry("2019-12-22 07:47:42 +0100", True),
            TestEntry("2019-12-16 09:47:42 +0100", True),
            TestEntry("2019-12-15 19:47:42 +0100", False),
            TestEntry("2019-12-13 10:47:42 +0100", False),
            TestEntry("2019-12-01 07:52:42 +0100", False),
            TestEntry("2019-11-07 08:07:42 +0100", False),
        ]
        existing_snapshots.sort(key=lambda entry: entry.ts_str)
        snap_collection = snapbtrfs.ExistingSnapshotsCollection()
        for entry in existing_snapshots:
            snap_collection.add(snapbtrfs.ExistingSnapshot(ts_str=entry.ts_str))
        snap_collection.mark_period(
            datetime.datetime(
                2019, 12, 26, 15, 1, 36, 123456, tzinfo=datetime.timezone.utc
            ),
            "daily",
            5,
        )
        for index in range(  # pylint: disable=consider-using-enumerate
            len(existing_snapshots)
        ):
            self.assertEqual(
                snap_collection.collection[index].ts_str,
                existing_snapshots[index].ts_str,
            )
            self.assertEqual(
                snap_collection.collection[index].is_kept,
                existing_snapshots[index].is_kept,
            )
