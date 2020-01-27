# lxc-vagrantize

This repository contains a set of scripts for creating base boxes for usage with
[vagrant-lxc](https://github.com/fgrehm/vagrant-lxc) 1.0+.

It is derived from https://github.com/fgrehm/vagrant-lxc-base-boxes. It is a rewrite in Python.

## What distros / versions can I build with this?

* Debian
  - Jessie, 8
  - Stretch, 9
  - Buster, 10
* Ubuntu
  - 16.04
  - 18.04
  - 18.10
  - 19.04
  - 19.10
* Fedora
  - 29
  - 30
  - 31
* Alpine
  - 3.10
* CentOS
  - 7
  - 8

## Building the boxes

In order to build the boxes you need to have the `lxc` installed.

```sh
git clone https://github.com/godfryd/lxc-vagrantizer
cd lxc-vagrantizer
./lxc-vagrantizer build -s debian -r 8
```

Example:

[![demo](https://asciinema.org/a/220315.svg)](https://asciinema.org/a/220315?autoplay=1)

## Pre built base boxes

| Distribution | VagrantCloud box |
| ------------ | ---------------- |
| Debian 8 Jessie | [godfryd/lxc-debian-8](https://vagrantcloud.com/godfryd/lxc-debian-8) |
| Debian 9 Stretch | [godfryd/lxc-debian-9](https://vagrantcloud.com/godfryd/lxc-debian-9) |
| Debian 10 Buster | [godfryd/lxc-debian-10](https://vagrantcloud.com/godfryd/lxc-debian-10) |
| Ubuntu 16.04 | [godfryd/lxc-ubuntu-16.04](https://vagrantcloud.com/godfryd/lxc-ubuntu-16.04) |
| Ubuntu 18.04 | [godfryd/lxc-ubuntu-18.04](https://vagrantcloud.com/godfryd/lxc-ubuntu-18.04) |
| Ubuntu 18.10 | [godfryd/lxc-ubuntu-18.10](https://vagrantcloud.com/godfryd/lxc-ubuntu-18.10) |
| Ubuntu 19.04 | [godfryd/lxc-ubuntu-19.04](https://vagrantcloud.com/godfryd/lxc-ubuntu-19.04) |
| Ubuntu 19.10 | [godfryd/lxc-ubuntu-19.10](https://vagrantcloud.com/godfryd/lxc-ubuntu-19.10) |
| Fedora 29 | [godfryd/lxc-fedora-29](https://vagrantcloud.com/godfryd/lxc-fedora-29) |
| Fedora 30 | [godfryd/lxc-fedora-30](https://vagrantcloud.com/godfryd/lxc-fedora-30) |
| Fedora 31 | [godfryd/lxc-fedora-31](https://vagrantcloud.com/godfryd/lxc-fedora-31) |
| Alpine 3.10 | [godfryd/lxc-alpine-3.10](https://vagrantcloud.com/godfryd/lxc-alpine-3.10) |
| CentOS 7 | [godfryd/lxc-centos-7](https://vagrantcloud.com/godfryd/lxc-centos-7) |
| CentOS 8 | [godfryd/lxc-centos-8](https://vagrantcloud.com/godfryd/lxc-centos-8) |


## What makes up for a vagrant-lxc base box?

See [vagrant-lxc/BOXES.md](https://github.com/fgrehm/vagrant-lxc/blob/master/BOXES.md)


## Known issues

TBD
