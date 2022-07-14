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
  - 20.04
  - 20.10
  - 21.04
  - 21.10
  - 22.04
* Fedora
  - 29
  - 30
  - 31
  - 32
  - 33
  - 34
* Alpine
  - 3.10
  - 3.11
  - 3.12
  - 3.13
  - 3.14
  - 3.15
  - 3.16
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
| Debian 8 Jessie | [isc/lxc-debian-8](https://vagrantcloud.com/isc/lxc-debian-8) |
| Debian 9 Stretch | [isc/lxc-debian-9](https://vagrantcloud.com/isc/lxc-debian-9) |
| Debian 10 Buster | [isc/lxc-debian-10](https://vagrantcloud.com/isc/lxc-debian-10) |
| Ubuntu 16.04 | [isc/lxc-ubuntu-16.04](https://vagrantcloud.com/isc/lxc-ubuntu-16.04) |
| Ubuntu 18.04 | [isc/lxc-ubuntu-18.04](https://vagrantcloud.com/isc/lxc-ubuntu-18.04) |
| Ubuntu 18.10 | [isc/lxc-ubuntu-18.10](https://vagrantcloud.com/isc/lxc-ubuntu-18.10) |
| Ubuntu 19.04 | [isc/lxc-ubuntu-19.04](https://vagrantcloud.com/isc/lxc-ubuntu-19.04) |
| Ubuntu 19.10 | [isc/lxc-ubuntu-19.10](https://vagrantcloud.com/isc/lxc-ubuntu-19.10) |
| Ubuntu 20.04 | [isc/lxc-ubuntu-20.04](https://vagrantcloud.com/isc/lxc-ubuntu-20.04) |
| Ubuntu 20.10 | [isc/lxc-ubuntu-20.10](https://vagrantcloud.com/isc/lxc-ubuntu-20.10) |
| Ubuntu 21.04 | [isc/lxc-ubuntu-21.04](https://vagrantcloud.com/isc/lxc-ubuntu-21.04) |
| Ubuntu 21.10 | [MonkZ/lxc-ubuntu-21.10](https://vagrantcloud.com/MonkZ/lxc-ubuntu-21.10) |
| Ubuntu 22.04 | [MonkZ/lxc-ubuntu-22.04](https://vagrantcloud.com/MonkZ/lxc-ubuntu-22.04) |
| Fedora 29 | [isc/lxc-fedora-29](https://vagrantcloud.com/isc/lxc-fedora-29) |
| Fedora 30 | [isc/lxc-fedora-30](https://vagrantcloud.com/isc/lxc-fedora-30) |
| Fedora 31 | [isc/lxc-fedora-31](https://vagrantcloud.com/isc/lxc-fedora-31) |
| Alpine 3.10 | [isc/lxc-alpine-3.10](https://vagrantcloud.com/isc/lxc-alpine-3.10) |
| Alpine 3.11 | [isc/lxc-alpine-3.11](https://vagrantcloud.com/isc/lxc-alpine-3.11) |
| Alpine 3.12 | [isc/lxc-alpine-3.12](https://vagrantcloud.com/isc/lxc-alpine-3.12) |
| Alpine 3.13 | [isc/lxc-alpine-3.13](https://vagrantcloud.com/isc/lxc-alpine-3.13) |
| Alpine 3.14 | [isc/lxc-alpine-3.14](https://vagrantcloud.com/isc/lxc-alpine-3.14) |
| Alpine 3.15 | [isc/lxc-alpine-3.15](https://vagrantcloud.com/isc/lxc-alpine-3.15) |
| Alpine 3.16 | [isc/lxc-alpine-3.16](https://vagrantcloud.com/isc/lxc-alpine-3.16) |
| CentOS 7 | [isc/lxc-centos-7](https://vagrantcloud.com/isc/lxc-centos-7) |
| CentOS 8 | [isc/lxc-centos-8](https://vagrantcloud.com/isc/lxc-centos-8) |


## What makes up for a vagrant-lxc base box?

See [vagrant-lxc/BOXES.md](https://github.com/fgrehm/vagrant-lxc/blob/master/BOXES.md)
