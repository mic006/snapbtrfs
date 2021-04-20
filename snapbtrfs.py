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

"""Perform periodic snapshots of btrfs subvolumes.

The script:
- takes snapshot of btrfs subvolumes with the desired periodicity
- keeps the wanted number of past snapshots, per periodicity
- deletes the old extra snapshots

It allows to automatically keep an history of btrfs subvolumes
(allowing to rollback some unwanted modification or deletion).

The configuration is done in /etc/snapbtrfs.conf.yaml, in YAML format.

This is a one-shot script and not a daemon: it performs the needed actions and exits.
It has to be called periodically, by a systemd timer or by cron (/etc/cron.hourly typically).

VERSION:
"""

import bisect
import datetime
import functools
import os
import pathlib
import re
import subprocess

import yaml

# debug mode
DEBUG = True

# location of configuration file
if DEBUG:
    CFG_FILE = "snapbtrfs.conf.yaml"
else:
    CFG_FILE = "/etc/snapbtrfs.conf.yaml"

# keys used for period configuration
PERIOD_KEYS = (
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "yearly",
)


class DateTimeUtil:
    """
    Helper functions for datetime manipulation
    """

    @staticmethod
    def round_beginning_hour(ts: datetime.datetime) -> datetime.datetime:
        """
        Round to the beginning of the current hour
        Note: no concern with localtime / DST (at least for whole hour timezones)
        """
        return ts.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def round_beginning_day(ts: datetime.datetime) -> datetime.datetime:
        """
        Round to the beginning of the current day
        Note: we want hour=0 in localtime, even for DST switch day
        """
        ts = DateTimeUtil.round_beginning_hour(ts)
        local = ts.astimezone()
        if local.hour == 0:
            return ts
        # remove local hours
        ts -= datetime.timedelta(hours=local.hour)
        local = ts.astimezone()
        if local.hour == 0:
            return ts
        # DST adjustment
        if local.hour == 1:
            return ts - datetime.timedelta(hours=1)
        return ts + datetime.timedelta(hours=1)

    @staticmethod
    def round_beginning_week(ts: datetime.datetime) -> datetime.datetime:
        """
        Round to the beginning of the current week (Monday)
        Note: we want hour=0, weekday=0 in localtime
        """
        ts = DateTimeUtil.round_beginning_day(ts)
        local = ts.astimezone()
        weekday = local.weekday()
        if weekday == 0:
            return ts
        # remove the needed days, but keeping half a day to protect for DST switch
        ts -= datetime.timedelta(hours=24 * (weekday - 1) + 12)
        return DateTimeUtil.round_beginning_day(ts)

    @staticmethod
    def round_beginning_month(ts: datetime.datetime) -> datetime.datetime:
        """
        Round to the beginning of the current month
        Note: we want hour=0, day=1 in localtime
        """
        ts = DateTimeUtil.round_beginning_day(ts)
        local = ts.astimezone()
        if local.day == 1:
            return ts
        # remove the needed days, but keeping half a day to protect for DST switch
        ts -= datetime.timedelta(hours=24 * (local.day - 2) + 12)
        return DateTimeUtil.round_beginning_day(ts)

    @staticmethod
    def round_beginning_year(ts: datetime.datetime) -> datetime.datetime:
        """
        Round to the beginning of the current year
        Note: we want hour=0, day=1, month=1 in localtime
        """
        ts = DateTimeUtil.round_beginning_day(ts)
        local = ts.astimezone()
        if (local.month, local.day) == (1, 1):
            return ts
        # remove the needed days, but keeping half a day to protect for DST switch
        yday = local.toordinal() - datetime.datetime(local.year, 1, 1).toordinal()
        ts -= datetime.timedelta(hours=24 * (yday - 1) + 12)
        return DateTimeUtil.round_beginning_day(ts)

    @staticmethod
    def prev_hour(ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous hour boundary
        Note: no concern with localtime / DST (at least for whole hour timezones)
        """
        if (ts.minute, ts.second, ts.microsecond) != (0, 0, 0):
            return DateTimeUtil.round_beginning_hour(ts)
        return ts - datetime.timedelta(hours=1)

    @staticmethod
    def prev_day(ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous day boundary
        """
        local = ts.astimezone()
        if (local.hour, local.minute, local.second, local.microsecond) != (0, 0, 0, 0):
            return DateTimeUtil.round_beginning_day(ts)
        return DateTimeUtil.round_beginning_day(ts - datetime.timedelta(hours=12))

    @staticmethod
    def prev_week(ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous week boundary
        """
        local = ts.astimezone()
        if (
            local.weekday(),
            local.hour,
            local.minute,
            local.second,
            local.microsecond,
        ) != (0, 0, 0, 0, 0):
            return DateTimeUtil.round_beginning_week(ts)
        return DateTimeUtil.round_beginning_week(ts - datetime.timedelta(days=1))

    @staticmethod
    def prev_month(ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous month boundary
        """
        local = ts.astimezone()
        if (local.day, local.hour, local.minute, local.second, local.microsecond) != (
            1,
            0,
            0,
            0,
            0,
        ):
            return DateTimeUtil.round_beginning_month(ts)
        return DateTimeUtil.round_beginning_month(ts - datetime.timedelta(days=1))

    @staticmethod
    def prev_year(ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous year boundary
        """
        local = ts.astimezone()
        if (
            local.month,
            local.day,
            local.hour,
            local.minute,
            local.second,
            local.microsecond,
        ) != (1, 1, 0, 0, 0, 0):
            return DateTimeUtil.round_beginning_year(ts)
        return DateTimeUtil.round_beginning_year(ts - datetime.timedelta(days=1))

    map_prev_period = {
        "hourly": prev_hour.__func__,
        "daily": prev_day.__func__,
        "weekly": prev_week.__func__,
        "monthly": prev_month.__func__,
        "yearly": prev_year.__func__,
    }

    @staticmethod
    def prev_period(period: str, ts: datetime.datetime) -> datetime.datetime:
        """
        Return previous boundary for the given period
        """
        return DateTimeUtil.map_prev_period[period](ts)


@functools.total_ordering
class ExistingSnapshot:
    """
    Represents an existing snapshot
    """

    env = None  # cache

    def __init__(
        self,
        path: pathlib.Path = None,
        ts: datetime.datetime = None,
        ts_str: str = None,
    ):
        if ts:
            self.ts = ts
        else:
            if path:
                self.path = path
                self.ts_str = ExistingSnapshot.get_snapshot_creation_time_str(self.path)
            else:
                self.ts_str = ts_str
            self.ts = datetime.datetime.strptime(self.ts_str, "%Y-%m-%d %H:%M:%S %z")

        # key = round ts to previous hour
        self.key = DateTimeUtil.round_beginning_hour(self.ts)
        self.is_kept = False

    def __lt__(self, other):
        return self.key < other.key

    def __eq__(self, other):
        return self.key == other.key

    def keep(self) -> None:
        """
        Mark the ExistingSnapshot as 'to be kept'
        """
        self.is_kept = True

    @classmethod
    def get_snapshot_creation_time_str(cls, path: pathlib.Path) -> str:
        """
        Get creation time of the given snapshot
        """
        if cls.env is None:
            cls.env = os.environ.copy()
            cls.env[  # pylint: disable=unsupported-assignment-operation
                "LANG"
            ] = "C"  # enforce LANG=C to avoid any translation
        result = subprocess.run(
            ["btrfs", "subvolume", "show", path.as_posix()],
            check=True,
            text=True,
            capture_output=True,
            env=cls.env,
        )
        return re.search(
            r"^\s*Creation time:\s*(\w.*)$", result.stdout, flags=re.MULTILINE
        ).group(1)


class ExistingSnapshotsCollection:
    """
    Collection of ExistingSnapshot
    """

    def __init__(self):
        self.collection = []
        self.sorted = True

    def add(self, snap: ExistingSnapshot) -> None:
        """
        Add existing snapshot in the collection
        """
        self.collection.append(snap)
        self.sorted = False

    def sort(self) -> None:
        """
        Sort the existing snapshots by date
        """
        if not self.sorted:
            self.collection.sort(key=lambda snap: snap.key)
            self.sorted = True

    def find_oldest_in_window(
        self, begin: datetime.datetime, end: datetime.datetime
    ) -> ExistingSnapshot:
        """
        Find oldest snapshot in the given window:
        begin <= snap.key < end
        """
        self.sort()
        index = bisect.bisect_left(self.collection, ExistingSnapshot(ts=begin))
        if index >= len(self.collection):
            return None  # no element whose snap.key >= begin
        snap = self.collection[index]
        if snap.key < end:
            return snap
        return None

    def mark_period(self, now: datetime.datetime, period: str, nb_kept: int) -> None:
        """
        Mark snapshots to be kept for a period type
        """
        self.sort()
        end = now
        while nb_kept > 0 and self.collection and end >= self.collection[0].ts:
            begin = DateTimeUtil.prev_period(period, end)
            snap = self.find_oldest_in_window(begin, end)
            if snap:
                snap.keep()
                nb_kept -= 1
            end = begin

    def has_snapshop_in_last_period(self, now: datetime.datetime, period: str) -> bool:
        """
        Indicate if the collection already contains a snapshot in the given period
        """
        return (
            self.find_oldest_in_window(DateTimeUtil.prev_period(period, now), now)
            is not None
        )


def system_run(args) -> None:
    """
    Run the provided command
    """
    if DEBUG:
        print(f"DBG: system_run '{' '.join(args)}'")
    else:
        subprocess.run(args, check=True)


def main():  # pylint: disable=too-many-locals
    """
    snapbtrfs main function
    """
    # read configuration
    with open(CFG_FILE, mode="r") as cfgfile:
        config = yaml.load(cfgfile, Loader=yaml.CSafeLoader)

    # set umask if configured
    if config["umask"]:
        os.umask(int(config["umask"], 0))

    # get current ts
    now = datetime.datetime.now(datetime.timezone.utc)
    now_local = now.astimezone()

    # manage each btrfs mount point
    for btrfs_root_str, volumes in config["volumes"].items():
        btrfs_root = pathlib.Path(btrfs_root_str)
        btrfs_snaps = btrfs_root / config["snapshot_dir"]

        # manage each configured volume
        for volume in volumes:
            # get volume configuration
            # starts from 'default' configuration
            volume_cfg = dict(config.get("default", {}))
            # and add volume specific configuration
            volume_cfg.update(volume)

            # get all snapshots
            btrfs_snaps_vol = btrfs_snaps / volume_cfg["path"]
            snap_collection = ExistingSnapshotsCollection()
            for snap_file in os.listdir(btrfs_snaps_vol):
                snap_collection.add(ExistingSnapshot(path=btrfs_snaps_vol / snap_file))

            # check if a new snapshot has to be taken
            if not all(
                snap_collection.has_snapshop_in_last_period(now, period)
                for period in PERIOD_KEYS
                if volume_cfg.get(period, 0) > 0
            ):
                # determine which shall be kept / deleted
                for period in PERIOD_KEYS:
                    if period in volume_cfg:
                        snap_collection.mark_period(now, period, volume_cfg[period])

                # perform snapshot
                new_snap_path = btrfs_snaps_vol / f"{now_local:%F-%T}"
                print(f"Taking snapshot {new_snap_path}")
                system_run(
                    [
                        "btrfs",
                        "subvolume",
                        "snapshot",
                        "-r",
                        (btrfs_root / volume_cfg["path"]).as_posix(),
                        new_snap_path.as_posix(),
                    ]
                )

                # delete snapshots to be deleted
                for snap in snap_collection.collection:
                    if not snap.is_kept:
                        print(f"Deleting snapshot {snap.path}")
                        system_run(
                            ["btrfs", "subvolume", "delete", snap.path.as_posix()]
                        )


if __name__ == "__main__":
    main()
