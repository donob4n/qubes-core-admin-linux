#
# This is the SPEC file for creating binary RPMs for the Dom0.
#
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2013  Marek Marczykowski  <marmarek@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%{!?version: %define version %(cat version)}

%define _dracutmoddir	/usr/lib/dracut/modules.d
%if %{fedora} < 17
%define _dracutmoddir   /usr/share/dracut/modules.d
%endif

Name:		qubes-core-dom0-linux
Version:	%{version}
Release:	1%{?dist}
Summary:	Linux-specific files for Qubes dom0

Group:		Qubes
Vendor:		Invisible Things Lab
License:	GPL
URL:		http://www.qubes-os.org

BuildRequires:  ImageMagick
BuildRequires:  pandoc
BuildRequires:  qubes-utils-devel >= 3.1.3
BuildRequires:  qubes-libvchan-devel
Requires:	qubes-core-dom0
Requires:	python3-qubesadmin
Requires:	qubes-core-admin-client
Requires:	qubes-utils >= 3.1.3
Requires:	qubes-utils-libs >= 4.0.16
Conflicts:	qubes-core-dom0 < 4.0.23
Requires:	%{name}-kernel-install
Requires:	xdotool

%define _builddir %(pwd)

%description
Linux customizations required to use system as Qubes dom0.
Additionally some graphical elements for every Linux desktop envirnment (icons,
appmenus etc).

%package kernel-install
Summary:	Kernel install hook for Xen-based system

# get rid of os-prober, it tries to mount and parse all the block devices in
# the system, including loop*
Provides: os-prober
Obsoletes: os-prober

%description kernel-install
Kernel install hook for Xen-based system.

%prep
# we operate on the current directory, so no need to unpack anything
# symlink is to generate useful debuginfo packages
rm -f %{name}-%{version}
ln -sf . %{name}-%{version}
%setup -T -D

%build
(cd dom0-updates; make)
(cd qrexec; make)
(cd file-copy-vm; make)
(cd doc; make manpages)

%install

## Appmenus
install -d $RPM_BUILD_ROOT/etc/qubes-rpc/policy
cp qubesappmenus/qubes.SyncAppMenus.policy $RPM_BUILD_ROOT/etc/qubes-rpc/policy/qubes.SyncAppMenus

### Dom0 updates
install -D dom0-updates/qubes-dom0-updates.cron $RPM_BUILD_ROOT/etc/cron.daily/qubes-dom0-updates.cron
install -D dom0-updates/qubes-dom0-update $RPM_BUILD_ROOT/usr/bin/qubes-dom0-update
install -D dom0-updates/qubes-receive-updates $RPM_BUILD_ROOT/usr/libexec/qubes/qubes-receive-updates
install -D dom0-updates/patch-dnf-yum-config $RPM_BUILD_ROOT/usr/lib/qubes/patch-dnf-yum-config
install -m 0644 -D dom0-updates/qubes-cached.repo $RPM_BUILD_ROOT/etc/yum.real.repos.d/qubes-cached.repo
install -D dom0-updates/qfile-dom0-unpacker $RPM_BUILD_ROOT/usr/libexec/qubes/qfile-dom0-unpacker
install -m 0644 -D dom0-updates/qubes.ReceiveUpdates $RPM_BUILD_ROOT/etc/qubes-rpc/qubes.ReceiveUpdates
install -m 0664 -D dom0-updates/qubes.ReceiveUpdates.policy $RPM_BUILD_ROOT/etc/qubes-rpc/policy/qubes.ReceiveUpdates

install -d $RPM_BUILD_ROOT/var/lib/qubes/updates

# Qrexec
mkdir -p $RPM_BUILD_ROOT/usr/bin $RPM_BUILD_ROOT/usr/sbin
install qrexec/qrexec-daemon $RPM_BUILD_ROOT/usr/sbin/
install qrexec/qrexec-client $RPM_BUILD_ROOT/usr/bin/
# XXX: Backward compatibility
ln -s ../../bin/qrexec-client $RPM_BUILD_ROOT/usr/lib/qubes/qrexec-client
ln -s ../../sbin/qrexec-daemon $RPM_BUILD_ROOT/usr/lib/qubes/qrexec-daemon
cp qrexec/qubes-rpc-multiplexer $RPM_BUILD_ROOT/usr/lib/qubes

### pm-utils
mkdir -p $RPM_BUILD_ROOT/usr/lib64/pm-utils/sleep.d
cp pm-utils/52qubes-pause-vms $RPM_BUILD_ROOT/usr/lib64/pm-utils/sleep.d/
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system
cp pm-utils/qubes-suspend.service $RPM_BUILD_ROOT/usr/lib/systemd/system/

### Dracut module
mkdir -p $RPM_BUILD_ROOT/etc/dracut.conf.d
cp dracut/dracut.conf.d/* $RPM_BUILD_ROOT/etc/dracut.conf.d/

mkdir -p $RPM_BUILD_ROOT%{_dracutmoddir}
cp -r dracut/modules.d/* $RPM_BUILD_ROOT%{_dracutmoddir}/

### Others
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
install -m 0644 -D system-config/limits-qubes.conf $RPM_BUILD_ROOT/etc/security/limits.d/99-qubes.conf
install -D system-config/cpufreq-xen.modules $RPM_BUILD_ROOT/etc/sysconfig/modules/cpufreq-xen.modules
install -m 0440 -D system-config/qubes.sudoers $RPM_BUILD_ROOT/etc/sudoers.d/qubes
install -D system-config/polkit-1-qubes-allow-all.rules $RPM_BUILD_ROOT/etc/polkit-1/rules.d/00-qubes-allow-all.rules
install -D system-config/qubes-dom0.modules $RPM_BUILD_ROOT/etc/sysconfig/modules/qubes-dom0.modules
install -D system-config/qubes-sync-clock.cron $RPM_BUILD_ROOT/etc/cron.d/qubes-sync-clock.cron
install -d $RPM_BUILD_ROOT/etc/udev/rules.d
install -m 644 system-config/00-qubes-ignore-devices.rules $RPM_BUILD_ROOT/etc/udev/rules.d/
install -m 644 system-config/12-qubes-ignore-lvm-devices.rules $RPM_BUILD_ROOT/etc/udev/rules.d/
install -m 644 -D system-config/disable-lesspipe.sh $RPM_BUILD_ROOT/etc/profile.d/zz-disable-lesspipe.sh
install -m 755 -D system-config/kernel-grub2.install $RPM_BUILD_ROOT/usr/lib/kernel/install.d/90-grub2.install
install -m 755 -D system-config/kernel-xen-efi.install $RPM_BUILD_ROOT/usr/lib/kernel/install.d/90-xen-efi.install
install -m 755 -D system-config/kernel-remove-bls.install $RPM_BUILD_ROOT/usr/lib/kernel/install.d/99-remove-bls.install
install -m 644 -D system-config/75-qubes-dom0.preset \
    $RPM_BUILD_ROOT/usr/lib/systemd/system-preset/75-qubes-dom0.preset
install -m 644 -D system-config/99-qubes-default-disable.preset \
    $RPM_BUILD_ROOT/usr/lib/systemd/system-preset/99-qubes-default-disable.preset
install -d $RPM_BUILD_ROOT/etc/dnf/protected.d
install -m 0644 system-config/dnf-protected-qubes-core-dom0.conf  \
        $RPM_BUILD_ROOT/etc/dnf/protected.d/qubes-core-dom0.conf


touch $RPM_BUILD_ROOT/var/lib/qubes/.qubes-exclude-block-devices

# file copy to VM
install -m 755 file-copy-vm/qfile-dom0-agent $RPM_BUILD_ROOT/usr/lib/qubes/
install -m 755 file-copy-vm/qvm-copy-to-vm $RPM_BUILD_ROOT/usr/bin/
ln -s qvm-copy-to-vm $RPM_BUILD_ROOT/usr/bin/qvm-move-to-vm

### Documentation
(cd doc; make DESTDIR=$RPM_BUILD_ROOT install)

%pre
if ! grep -q ^qubes: /etc/group ; then
		groupadd qubes
fi

%post

/usr/lib/qubes/patch-dnf-yum-config

systemctl enable qubes-suspend.service >/dev/null 2>&1

%preun
if [ "$1" = 0 ] ; then
	# no more packages left

    systemctl disable qubes-suspend.service > /dev/null 2>&1
fi

%triggerin -- PackageKit
# dom0 have no network, but still can receive updates (qubes-dom0-update)
sed -i 's/^UseNetworkHeuristic=.*/UseNetworkHeuristic=false/' /etc/PackageKit/PackageKit.conf

%triggerin -- xorg-x11-drv-vmmouse
# Remove unnecessary udev rules that causes problems in dom0 (#605)
rm -f /lib/udev/rules.d/69-xorg-vmmouse.rules

%triggerin -- grub2-tools
chmod -x /etc/grub.d/10_linux

%files
/etc/qubes-rpc/policy/qubes.SyncAppMenus
# Dom0 updates
/etc/cron.daily/qubes-dom0-updates.cron
/etc/yum.real.repos.d/qubes-cached.repo
/usr/bin/qubes-dom0-update
/usr/lib/qubes/patch-dnf-yum-config
%attr(4750,root,qubes) /usr/libexec/qubes/qfile-dom0-unpacker
/usr/libexec/qubes/qubes-receive-updates
/etc/qubes-rpc/qubes.ReceiveUpdates
%attr(0664,root,qubes) %config(noreplace) /etc/qubes-rpc/policy/qubes.ReceiveUpdates
%attr(0770,root,qubes) %dir /var/lib/qubes/updates
# Dracut module
/etc/dracut.conf.d/*
%dir %{_dracutmoddir}/90qubes-pciback
%{_dracutmoddir}/90qubes-pciback/*
%dir %{_dracutmoddir}/90extra-modules
%{_dracutmoddir}/90extra-modules/*
# Qrexec
/usr/sbin/qrexec-daemon
/usr/bin/qrexec-client
/usr/lib/qubes/qubes-rpc-multiplexer
# compat symlinks
/usr/lib/qubes/qrexec-client
/usr/lib/qubes/qrexec-daemon
# file copy
/usr/bin/qvm-copy-to-vm
/usr/bin/qvm-move-to-vm
/usr/lib/qubes/qfile-dom0-agent
# pm-utils
/usr/lib64/pm-utils/sleep.d/52qubes-pause-vms
/usr/lib/systemd/system/qubes-suspend.service
# Others
/etc/sysconfig/modules/qubes-dom0.modules
/etc/sysconfig/modules/cpufreq-xen.modules
/etc/sudoers.d/qubes
/etc/polkit-1/rules.d/00-qubes-allow-all.rules
/etc/security/limits.d/99-qubes.conf
%config /etc/udev/rules.d/00-qubes-ignore-devices.rules
%config /etc/udev/rules.d/12-qubes-ignore-lvm-devices.rules
%attr(0644,root,root) /etc/cron.d/qubes-sync-clock.cron
%config(noreplace) /etc/profile.d/zz-disable-lesspipe.sh
%config(noreplace) /etc/dnf/protected.d/qubes-core-dom0.conf
/usr/lib/systemd/system-preset/75-qubes-dom0.preset
/usr/lib/systemd/system-preset/99-qubes-default-disable.preset
/var/lib/qubes/.qubes-exclude-block-devices
# Man
%{_mandir}/man1/qvm-*.1*
%{_mandir}/man1/qubes-*.1*

%files kernel-install
/usr/lib/kernel/install.d/90-grub2.install
/usr/lib/kernel/install.d/90-xen-efi.install
/usr/lib/kernel/install.d/99-remove-bls.install

%changelog
