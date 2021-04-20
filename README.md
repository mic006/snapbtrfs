# snapbtrfs

`snapbtrfs` is a utility to perform and manage periodic snapshots of btrfs subvolumes.

## Purpose

[Btrfs](https://btrfs.wiki.kernel.org/index.php/Main_Page) filesystem allows to easily take a read-only snapshot of any [subvolume](https://btrfs.wiki.kernel.org/index.php/Manpage/btrfs-subvolume).

`snapbtrfs` automatizes the management of snapshots:
- takes snapshot of btrfs subvolumes with the desired periodicity
- keeps the wanted number of past snapshots, per periodicity
- deletes the old extra snapshots

Note: these snapshots are NOT a backup, any damage to the disk / filesystem can corrupt all snapshots.

## Configuration

The configuration is done in `/etc/snapbtrfs.conf.yaml`, in YAML format.

You have to configure:
- the btrfs root mount point(s)
- the subvolumes to snapshot
- how many snapshots you want to keep, for each periodicity

It allows to automatically keep an history of btrfs subvolumes
(allowing to rollback some unwanted modification or deletion),
with frequent snapshots for the recent past, and less snapshots as time goes by
(somehow a logarithmic history).

## Install

1. Define your configuration in `/etc/snapbtrfs.conf.yaml`.
2. Copy `snapbtrfs.service` and `snapbtrfs.timer` to `/etc/systemd/system`
3. Enable the timer: `systemctl enable snapbtrfs.timer`

## Dependencies

- python-yaml library for yaml configuration reading

## Thanks

- the whole open source community for all the wonderful tools we are using everyday
