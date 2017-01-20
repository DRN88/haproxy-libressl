%define libressl_version 2.4.4
%define haproxy_extraoptions USE_REGPARM=1 USE_LINUX_SPLICE=1 USE_LIBCRYPT=1 USE_LINUX_TPROXY=1 USE_ZLIB=1 USE_PCRE_JIT=1 USE_PCRE=1 USE_TFO=1

%define haproxy_user     haproxy
%define haproxy_group    %{haproxy_user}
%define haproxy_home     %{_localstatedir}/lib/haproxy
%define haproxy_confdir  %{_sysconfdir}/haproxy
%define haproxy_datadir  %{_datadir}/haproxy

%global _hardened_build 1

Name:           haproxy
Version:        1.7.2
Release:        1%{?dist}
Summary:        TCP/HTTP proxy and load balancer for high availability environments

Group:          System Environment/Daemons
License:        GPLv2+

URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/1.7/src/haproxy-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.cfg
Source3:        %{name}.logrotate
Source4:        %{name}.sysconfig
Source5:        halog.1

Patch0:         halog-unused-variables.patch
#Patch1:         iprange-return-type.patch
#Patch2:         haproxy-tcp-user-timeout.patch

BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
#BuildRequires:  openssl-devel
BuildRequires:  systemd-units

BuildRequires: wget
BuildRequires: tar
BuildRequires: git
BuildRequires: patch
BuildRequires: autoconf
BuildRequires: make
BuildRequires: automake
BuildRequires: libtool
BuildRequires: gcc-c++

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
HAProxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
 - route HTTP requests depending on statically assigned cookies
 - spread load among several servers while assuring server persistence
   through the use of HTTP cookies
 - switch to backup servers in the event a main server fails
 - accept connections to special ports dedicated to service monitoring
 - stop accepting connections without breaking existing ones
 - add, modify, and delete HTTP headers in both directions
 - block requests matching particular patterns
 - report detailed status to authenticated users from a URI
   intercepted by the application

%prep

cd %{_sourcedir}
wget "https://github.com/libressl-portable/portable/archive/v%{libressl_version}.tar.gz" -O %{_sourcedir}/v%{libressl_version}.tar.gz
tar -xzf v%{libressl_version}.tar.gz
cd portable-%{libressl_version}
./autogen.sh
./configure --prefix=%{_sourcedir}/static-libressl-%{libressl_version} --enable-shared=no --enable-static=yes
make
make install

%setup -q
%patch0 -p0
#%patch1 -p0
#%patch2 -p1

%build
#regparm_opts=
#%ifarch %ix86 x86_64
#regparm_opts="USE_REGPARM=1"
#%endif

# Original build from centos 7 haproxy 1.5 SRPM
#%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18

# Static LibreSSL
%{__make} %{?_smp_mflags} ARCH=%{_target_cpu} TARGET="linux2628" USE_OPENSSL=1 SSL_INC=%{_sourcedir}/static-libressl-%{libressl_version}/include SSL_LIB=%{_sourcedir}/static-libressl-%{libressl_version}/lib ADDLIB="-ldl -lrt" %{haproxy_extraoptions}


pushd contrib/halog
%{__make} halog OPTIMIZE="%{optflags}"
popd

pushd contrib/iprange
%{__make} iprange OPTIMIZE="%{optflags}"
popd

%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix}
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1

%{__install} -p -D -m 0755 %{_builddir}/%{name}-%{version}/haproxy-systemd-wrapper %{buildroot}%{_sbindir}/haproxy-systemd-wrapper

%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}

for httpfile in $(find ./examples/errorfiles/ -type f)
do
    %{__install} -p -m 0644 $httpfile %{buildroot}%{haproxy_datadir}
done

%{__rm} -rf ./examples/errorfiles/

find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;

for textfile in $(find ./ -type f -name "*.txt" -o -name README)
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done

%pre
getent group %{haproxy_group} >/dev/null || \
       groupadd -g 188 -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
       useradd -u 188 -r -g %{haproxy_group} -d %{haproxy_home} \
       -s /sbin/nologin -c "haproxy" %{haproxy_user}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)
%doc doc/* examples/
%doc CHANGELOG LICENSE README ROADMAP VERSION
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_sbindir}/%{name}-systemd-wrapper
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}

%changelog
