%define name maniadrive
%define rname ManiaDrive
%define engine_name raydium
%define version 1.2
%define pre 0
%if %{pre}
%define release  0.%{pre}.3
%define fullversion %{version}-%{pre}
%else
%define release  13
%define fullversion %{version}
%endif
%define distname %{rname}-%{fullversion}-src
%define major 0
%define libname %mklibname %{name} %{major}

Summary: Arcade car game on acrobatic tracks
Name: %{name}
Version: %{version}
Release: %{release}
# svn export svn://raydium.org/raydium/trunk raydium-svn`date +%Y%m%d`
Source0: %{distname}.tar.bz2
Source1: %{name}.png
Source2: maniadrive.rpmlintrc
Patch0: raydium-1.01-svn20060728-build.patch
Patch1: ManiaDrive-1.1-src.dirs.patch
Patch3: ManiaDrive-1.1-src.safemode.patch
Patch4: ManiaDrive-1.1-src.home.patch
Patch5: ManiaDrive-1.2-src.fPIC.patch
Patch6: ManiaDrive-1.2-ode.patch
Patch7: ManiaDrive-1.2-key.patch
License: GPL
Group: Games/Arcade
Url: http://raydium.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: curl-devel
BuildRequires: jpeg-devel
BuildRequires: pkgconfig(xinerama)
BuildRequires: php-devel
BuildRequires: ode-devel
BuildRequires: pkgconfig(vorbis)
BuildRequires: glew-devel
BuildRequires: freealut-devel
BuildRequires: openal-devel
BuildRequires: pkgconfig(libv4l1)
Requires: maniadrive-data
Conflicts: maniadrive-data < 1.01-3mdv2007.0
Requires: glxinfo
Requires: php-curl
Requires: php-ini
Requires: php-soap
Requires: php-zlib


%description
ManiaDrive is a free clone of Trackmania, the great game from Nadéo
studio, and is an arcade car game on acrobatic tracks, with a quick
and nervous gameplay (tracks almost never exceed one minute), and
features a network mode, as the original.

Raydium is a game engine. It provides a set of functions which allow
quick and flexible games creation.
Functions covers things like player inputs (keyboard, mouse, joystick,
joypad, force feedback), rendering (3D objets, OSD (On Screen
Display)), time (a game must run at the exact same speed on every
computer), sound, ...

%prep
%setup -q -n %{distname}
%patch0 -p0 -b .build
%patch1 -p1 -b .dirs
%patch3 -p1 -b .safemode
%patch4 -p1 -b .home
%patch5 -p1 -b .fPIC
%patch6 -p1
%patch7 -p1

# php weird stuff, borrowed from thttpd-php.spec
cp /usr/src/php-devel/internal_functions.c .
cp %{_includedir}/php/ext/date/lib/timelib_config.h .
ln -s /usr/src/php-devel/ext .

%build
%make
for f in mania2 mania_drive mania_server; do
  # from odyncomp.sh
  gcc $f.c -g -Wall -DFORCE_LIBRAYDIUM -DBINDIR=\"%{_gamesbindir}\" %{optflags} -DGAMEDIR=\"%{_gamesdatadir}/%{name}\" -o $f.static libraydium.so -lphp5_common -lGL -lm `php-config --includes`
done

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_libdir}
cp -a lib%{engine_name}.so.* %{buildroot}%{_libdir}
install -d %{buildroot}%{_gamesbindir}
install -m755 mania*.static %{buildroot}%{_gamesbindir}

# This may not be required on future versions of the intel dri driver
# Previously, %{_gamesbindir}/%{name} was a symlink to %{_gamesbindir}/mania_drive.static
# https://bugs.freedesktop.org/show_bug.cgi?id=28002
# https://bugs.freedesktop.org/show_bug.cgi?id=28069
cat > %{buildroot}%{_gamesbindir}/%{name} << EOF
\`glxinfo | grep -q 'OpenGL renderer string: Mesa'\` && export LIBGL_ALWAYS_INDIRECT=true
exec %{_gamesbindir}/mania_drive.static "\$@"
EOF
chmod +x %{buildroot}%{_gamesbindir}/%{name}

install -d %{buildroot}%{_gamesdatadir}/%{name}
install -m644 *.php %{buildroot}%{_gamesdatadir}/%{name}

cp -a rayphp %{buildroot}%{_gamesdatadir}/%{name}

install -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/icons/%{name}.png

# https://qa.mandriva.com/show_bug.cgi?id=37748
rm -f %{buildroot}%{_gamesdatadir}/%{name}/php.ini
ln -sf %{_sysconfdir}/php.ini %{buildroot}%{_gamesdatadir}/%{name}/php.ini
ln -sf %{_gamesdatadir}/%{name}/rayphp %{buildroot}%{_gamesdatadir}/%{name}/rayphp/rayphp

install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=ManiaDrive
Comment=Arcade car game on acrobatic tracks
Exec=soundwrapper %{_gamesbindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
Categories=Game;ArcadeGame;X-MandrivaLinux-MoreApplications-Games-Arcade;
EOF

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_gamesbindir}/%{name}
%{_gamesbindir}/mania*.static
%{_libdir}/lib%{engine_name}.*
%dir %{_gamesdatadir}/%{name}/rayphp
%{_gamesdatadir}/%{name}/php.ini
%{_gamesdatadir}/%{name}/mania_*.php
%{_gamesdatadir}/%{name}/rayphp/*
%{_datadir}/icons/%{name}.png
%{_datadir}/applications/%{name}.desktop
