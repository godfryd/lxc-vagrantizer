#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import glob
import time
import json
import logging
import argparse
import platform
import datetime
import subprocess
import urllib.request
import multiprocessing

log = logging.getLogger()


SYSTEMS = {
    'fedora': ['27', '28', '29', '30'],
    'centos': ['7'],
    #'rhel': ['7', '8'],
    'rhel': ['8'],
    'ubuntu': ['16.04', '18.04', '18.10', '19.04'],
    'debian': ['8', '9', '10'],
    'alpine': ['3.10', 'edge'],
}


def red(txt):
    if sys.stdout.isatty():
        return '\033[1;31m%s\033[0;0m' % txt
    else:
        return txt

def green(txt):
    if sys.stdout.isatty():
        return '\033[0;32m%s\033[0;0m' % txt
    else:
        return txt

def blue(txt):
    if sys.stdout.isatty():
        return '\033[0;34m%s\033[0;0m' % txt
    else:
        return txt


def get_system_revision():
    system = platform.system()
    system, revision, _ = platform.dist()
    if system == 'debian':
        if revision.startswith('8.'):
            revision = '8'
    elif system == 'redhat':
        system = 'rhel'
        if revision.startswith('8.'):
            revision = '8'
    return system.lower(), revision


class ExecutionError(Exception): pass

def execute(cmd, timeout=60, cwd=None, env=None, raise_error=True, dry_run=False, quiet=False, check_times=False, capture=False):
    log.info('>>>>> Executing %s in %s', cmd, cwd if cwd else os.getcwd())
    if not check_times:
        timeout = None
    if dry_run:
        return 0

    p = subprocess.Popen(cmd, cwd=cwd, env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    t0 = time.time()
    t1 = time.time()
    output = ''
    while p.poll() is None and (timeout is None or t1 - t0 < timeout):
        line = p.stdout.readline()
        if line:
            if not quiet:
                l = line.decode(errors='ignore').strip()
                if not capture:
                    print(l + '\r')
                output += l + '\n'
        t1 = time.time()

    if p.poll() is None:
        raise ExecutionError('Execution timeout')
    exitcode = p.returncode

    if exitcode != 0 and raise_error:
        raise ExecutionError("The command return non-zero exitcode %s, cmd: '%s'" % (exitcode, cmd))
    return exitcode, output


class LXC(object):
    def __init__(self, system, revision):
        self.system = system
        self.revision = revision
        self.name = '%s-%s-bare' % (system, revision)

        rev_map = {
            'debian': {'8': 'jessie',
                       '9': 'stretch',
                       '10': 'buster'},
            'ubuntu': {'14.04': 'trusty',
                       '16.04': 'xenial',
                       '18.04': 'bionic',
                       '18.10': 'cosmic',
                       '19.04': 'disco',
                       '19.10': 'eoan'}
        }
        try:
            self.alt_revision = rev_map[system][revision]
        except:
            self.alt_revision = revision

    def create(self):

        cmd = 'bash -c "echo -e \'{system}\\n{revision}\\namd64\' | sudo lxc-create -n {name} -t download"'
        cmd = cmd.format(system=self.system, revision=self.alt_revision, name=self.name)
        execute(cmd)

    def start(self):
        if self.get_state() != 'RUNNING':
            execute('sudo lxc-start -d -n %s' % self.name)

    def stop(self):
        if self.get_state() != 'STOPPED':
            execute('sudo lxc-stop -n %s' % self.name)

    def is_present(self):
        exitcode, _ = execute("sudo lxc-ls -1|grep '^%s$'" % self.name, raise_error=False)
        return exitcode == 0

    def destroy(self):
        if not self.is_present():
            return
        self.stop()
        execute('sudo lxc-destroy -n %s' % self.name)

    def execute(self, cmd):
        execute('sudo lxc-attach -n %s -- %s' % (self.name, cmd))

    def get_container_dir(self):
        return os.path.join('/var/lib/lxc', self.name)

    def get_rootfs_dir(self):
        return os.path.join(self.get_container_dir(), 'rootfs')

    def get_state(self):
        ret, out = execute('sudo lxc-info -n %s -s' % self.name, capture=True)
        if 'STOPPED' in out:
            return 'STOPPED'
        elif 'RUNNING' in out:
            return 'RUNNING'
        else:
            print(out)
            raise NotImplementedError


def install_extras(lxc):
    log.info('Installing extras...')
    lxc.start()
    time.sleep(5)  # wait for network
    if lxc.system in ['debian', 'ubuntu']:
        lxc.execute('apt update')
        lxc.execute('apt upgrade -y')
        packages = ['vim', 'wget', 'openssh-server', 'ca-certificates', 'sudo', 'python3']
        if lxc.system == 'debian' and lxc.revision == '8' or lxc.system == 'ubuntu' and lxc.revision == '16.04':
            packages.extend(['dbus', 'libnss-myhostname'])
            lxc.execute('mkdir -p /etc/systemd/system/systemd-hostnamed.service.d')
            lxc.execute('bash -c "echo -e \'[Service]\\nPrivateDevices=no\\n\' > /etc/systemd/system/systemd-hostnamed.service.d/override.conf"')
        elif lxc.system == 'ubuntu' and lxc.revision == '14.04':
            lxc.execute('mount -o remount,ro /sys/fs/selinux')
        cmd = 'apt install -y '
        cmd += ' '.join(packages)
        lxc.execute(cmd)
    elif lxc.system in ['fedora']:
        lxc.execute('dnf upgrade -y')
        packages = ['vim-enhanced', 'wget', 'openssh-server', 'ca-certificates', 'sudo', 'python3']
        cmd = 'dnf install -y '
        cmd += ' '.join(packages)
        lxc.execute(cmd)
    elif lxc.system in ['centos']:
        time.sleep(5)  # 5secs more for network
        lxc.execute('yum upgrade -y')
        packages = ['vim-enhanced', 'wget', 'openssh-server', 'ca-certificates', 'sudo', 'python3']
        cmd = 'yum install -y '
        cmd += ' '.join(packages)
        lxc.execute(cmd)
    elif lxc.system in ['alpine']:
        lxc.execute('apk update')
        lxc.execute('apk upgrade')
        lxc.execute('apk add vim wget openssh ca-certificates sudo python3 bash')
        lxc.execute('rc-update add sshd')
    else:
        print(lxc.system)
        raise NotImplementedError
    log.info('Installing extras done.')


def clean(lxc):
    lxc.start()

    log.info('Cleaning...')
    if lxc.system in ['debian', 'ubuntu']:
        lxc.execute('apt-get clean')
    elif lxc.system in ['fedora']:
        lxc.execute('dnf clean packages')
    elif lxc.system in ['centos']:
        lxc.execute('yum clean packages')

    lxc.stop()

    rootfs = lxc.get_rootfs_dir()

    if lxc.system in ['debian', 'ubuntu']:
        execute('sudo rm -rf %s/var/lib/apt/lists/*' % rootfs)

    execute('sudo rm -rf %s/usr/share/doc' % rootfs)
    execute('sudo rm -rf %s/tmp/*' % rootfs)
    execute('sudo rm -f %s/var/lib/dhcp/*' % rootfs)


def setup_vagrant_user(lxc):
    vagrant_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key"

    log.info("Preparing vagrant user...")

    lxc.stop()
    rootfs_dir = lxc.get_rootfs_dir()

    # Create vagrant user
    exitcode, _ = execute("sudo grep -q 'vagrant' %s/etc/shadow" % rootfs_dir, raise_error=False)
    if exitcode == 0:
      log.info('Skipping vagrant user creation')
    #elif $(grep -q 'ubuntu' ${ROOTFS}/etc/shadow); then
    #  debug 'vagrant user does not exist, renaming ubuntu user...'
    #  mv ${ROOTFS}/home/{ubuntu,vagrant}
    #  chroot ${ROOTFS} usermod -l vagrant -d /home/vagrant ubuntu &>> ${LOG}
    #  chroot ${ROOTFS} groupmod -n vagrant ubuntu &>> ${LOG}
    #  echo -n 'vagrant:vagrant' | chroot ${ROOTFS} chpasswd
    #  log 'Renamed ubuntu user to vagrant and changed password.'
    #elif [ ${DISTRIBUTION} = 'centos' -o ${DISTRIBUTION} = 'fedora' ]; then
    #  debug 'Creating vagrant user...'
    #  chroot ${ROOTFS} useradd --create-home -s /bin/bash -u 1000 vagrant &>> ${LOG}
    #  echo -n 'vagrant:vagrant' | chroot ${ROOTFS} chpasswd
    #  sed -i 's/^Defaults\s\+requiretty/# Defaults requiretty/' $ROOTFS/etc/sudoers
    #  if [ ${RELEASE} -eq 6 ]; then
    #    info 'Disabling password aging for root...'
    #    # disable password aging (required on Centos 6)
    #    # pretend that password was changed today (won't fail during provisioning)
    #    chroot ${ROOTFS} chage -I -1 -m 0 -M 99999 -E -1 -d `date +%Y-%m-%d` root
    #  fi
    elif lxc.system in ['debian', 'ubuntu']:
        log.debug('Creating vagrant user...')
        if lxc.system == 'ubuntu':
            execute('sudo chroot %s userdel ubuntu' % rootfs_dir)
        execute('sudo chroot %s useradd --create-home -s /bin/bash vagrant' % rootfs_dir)
        execute('sudo chroot %s adduser vagrant sudo' % rootfs_dir)
        execute("bash -c \"echo -n 'vagrant:vagrant' | sudo chroot %s chpasswd\"" % rootfs_dir)
    elif lxc.system in ['fedora', 'centos']:
        log.debug('Creating vagrant user...')
        execute('sudo chroot %s useradd --create-home -s /bin/bash -u 1000 vagrant' % rootfs_dir)
        execute("bash -c \"echo -n 'vagrant:vagrant' | sudo chroot %s chpasswd\"" % rootfs_dir)
        execute("sudo sed -i 's/^Defaults\s\+requiretty/# Defaults requiretty/' %s/etc/sudoers" % rootfs_dir)
    elif lxc.system in ['alpine']:
        log.debug('Creating vagrant user...')
        execute('sudo chroot %s adduser -D vagrant' % rootfs_dir)
        execute("bash -c \"echo -n 'vagrant:vagrant' | sudo chroot %s chpasswd\"" % rootfs_dir)
        execute("bash -c \"echo -n 'vagrant ALL=(ALL) NOPASSWD: ALL' | sudo chroot %s tee /etc/sudoers.d/vagrant\"" % rootfs_dir)
    else:
        raise NotImplementedError

    # Configure SSH access
    ssh_dir = os.path.join(rootfs_dir, 'home/vagrant/.ssh')
    execute('sudo mkdir -p %s' % ssh_dir)
    execute("sudo bash -c 'echo \"%s\" > %s/authorized_keys'" % (vagrant_key, ssh_dir))
    execute("sudo chroot %s chown -R vagrant: /home/vagrant/.ssh" % rootfs_dir)
    log.info('SSH credentials configured for the vagrant user.')

    # Enable passwordless sudo for the vagrant user
    execute('sudo bash -c \'echo "vagrant ALL=(ALL) NOPASSWD:ALL" > %s/etc/sudoers.d/vagrant\'' % rootfs_dir)
    execute('sudo chmod 0440 %s/etc/sudoers.d/vagrant' % rootfs_dir)
    log.info('Sudoers file created.')

    log.info("Preparing vagrant user done.")


def package(lxc):
    pkg_path = '%s.box' % lxc.name
    pkg_path = os.path.abspath(os.path.join('work', pkg_path))
    log.info("Packaging '%s' to '%s'...", lxc.name, pkg_path)

    log.debug('Stopping container')
    lxc.stop()

    if not os.path.exists('work'):
        os.mkdir('work')

    if os.path.exists(pkg_path):
        os.unlink(pkg_path)

    working_dir = os.path.abspath(os.path.join('work', lxc.name))
    if os.path.exists(working_dir):
        execute('sudo rm -rf %s' % working_dir)
    os.mkdir(working_dir)

    log.info("Compressing container's rootfs")
    execute('sudo bash -c "cd %s && tar --numeric-owner --anchored --exclude=./rootfs/dev/log -czf %s/rootfs.tar.gz ./rootfs/*"' % (lxc.get_container_dir(), working_dir))

    # Prepare package contents
    log.info('Preparing box package contents')
    execute('sudo cp lxc-confs/%s-%s %s/lxc-config' % (lxc.system, lxc.revision, working_dir))
    execute('sudo chown `id -un`:`id -gn` *', cwd=working_dir)

    with open(os.path.join(working_dir, 'metadata.json'), 'w') as f:
        now = datetime.datetime.now()
        f.write('{\n')
        f.write('  "provider": "lxc",\n')
        f.write('  "version":  "1.0.0",\n')
        f.write('  "built-on": "%s"\n' % now.strftime('%c'))
        f.write('}\n')

    # Vagrant box!
    log.info('Packaging box')
    execute('tar -czf %s ./*' % pkg_path, cwd=working_dir)
    execute('sudo rm -rf %s' % working_dir)

    return pkg_path


def upload(org_name, system, revision, box_path):
    # retrieve metadata from the cloud
    box_name = "%s/lxc-%s-%s" % (org_name, system, revision)
    url = 'https://app.vagrantup.com/api/v1/box/' + box_name
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        data = json.loads(data)
    except:
        log.exception('ignored exception')
        data = None

    log.info(data)

    # establish latest version
    if data and 'versions' in data:
        latest_version = 0
        for ver in data['versions']:
            log.info(ver)
            provider_found = False
            for p in ver['providers']:
                if p['name'] == 'lxc':
                    provider_found = True
                    break
            if provider_found:
                v = int(ver['number'])
                if v > latest_version:
                    latest_version = v
    else:
        latest_version = 0

    # upload image to the cloud
    new_version = latest_version + 1

    cmd = "vagrant cloud publish -f -r %s %s lxc %s"
    cmd = cmd % (box_name, new_version, box_path)

    execute(cmd, timeout=60)


def list_systems():
    pass

def parse_args():
    parser = argparse.ArgumentParser(description='Kea develepment environment management tool.')

    parser.add_argument('command', choices=['build', 'attach', 'list-systems', 'ensure-lxc-vagrantizer-deps'],
                        help='Commands.')
    parser.add_argument('-s', '--system', default='all', choices=list(SYSTEMS.keys()) + ['all'],
                        help="Build is executed on selected system. If 'all' then build is executed several times on all systems. "
                        "If provider is 'local' then this option is ignored. Default is 'all'.")
    parser.add_argument('-r', '--revision', default='all',
                        help="Revision of selected system. If 'all' then build is executed several times "
                        "on all revisions of selected system. To list supported systems and their revisions invoke 'list-systems'. "
                        "Default is 'all'.")
    #parser.add_argument('-w', '--with', nargs='+', default=set(), choices=ALL_FEATURES,
    #                    help="Enabled, comma-separated features. Default is '%s'." % ' '.join(DEFAULT_FEATURES))
    #parser.add_argument('-x', '--without', nargs='+', default=set(), choices=ALL_FEATURES,
    #                    help="Disabled, comma-separated features. Default is ''.")
    parser.add_argument('-l', '--leave-system', action='store_true',
                        help='At the end of command do not destroy vagrant system. Default behavior is destroing the system.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Enable quiet mode.')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Print only what would be done.')
    parser.add_argument('-c', '--clean-start', action='store_true', help='If there is pre-existing system then it is destroyed first.')
    parser.add_argument('-i', '--check-times', action='store_true', help='Do not allow executing commands infinitelly.')
    parser.add_argument('-u', '--upload', help='Upload to Vagrant Cloud under indicated org name.')

    args = parser.parse_args()

    return args


def main():
    os.environ['LC_ALL'] = os.environ['LANG'] = 'C'

    args = parse_args()

    format = '[LXC-VAGRANTIZER]  %(asctime)-15s  %(message)s'
    logging.basicConfig(format=format, level=logging.DEBUG)

    if args.command == 'list-systems':
        list_systems()

    elif args.command == "build":

        if args.system == 'all':
            systems = SYSTEMS.keys()
        else:
            systems = [args.system]

        plan = []
        results = {}
        log.info('Build plan:')
        for system in systems:
            if args.revision == 'all':
                revisions = SYSTEMS[system]
            else:
                revisions = [args.revision]

            for revision in revisions:
                plan.append((system, revision))
                log.info(' - %s, %s', system, revision)
                results[(system, revision)] = (0, 'not run')

        fail = False
        for system, revision in plan:

            lxc = LXC(system, revision)
            try:
                lxc.destroy()
                lxc.create()
                install_extras(lxc)
                setup_vagrant_user(lxc)
                clean(lxc)
                box_path = package(lxc)
                if args.upload:
                    upload(args.upload, system, revision, box_path)
            except:
                log.exception('something went wrong')
                lxc.destroy()

    elif args.command == "ensure-lxc-vagrantizer-deps":
        ensure_lxc_vagrantizer_deps()


if __name__ == '__main__':
    main()
