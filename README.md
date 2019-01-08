# lxc-vagrantize

This repository contains a set of scripts for creating base boxes for usage with
[vagrant-lxc](https://github.com/fgrehm/vagrant-lxc) 1.0+.

It is derived from https://github.com/fgrehm/vagrant-lxc-base-boxes. It is a rewrite in Python.

## What distros / versions can I build with this?

* Debian
  - Jessie, 8
  - Stretch, 9
* Fedora
  - 29

## Building the boxes

In order to build the boxes you need to have the `lxc` installed.

```sh
git clone https://github.com/godfryd/lxc-vagrantizer
cd lxc-vagrantizer
./lxc-vagrantizer build -s debian -r 8
```

## Pre built base boxes

_**NOTE:** None of the base boxes below have a provisioner pre-installed_

| Distribution | VagrantCloud box |
| ------------ | ---------------- |
| Debian 8 Jessie | [godfryd/lxc-debian-8](https://vagrantcloud.com/godfryd/lxc-debian-8) |


## What makes up for a vagrant-lxc base box?

See [vagrant-lxc/BOXES.md](https://github.com/fgrehm/vagrant-lxc/blob/master/BOXES.md)


## Known issues

TBD