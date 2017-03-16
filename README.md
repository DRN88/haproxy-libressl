# haproxy-libressl
Open haproxy.spec first and learn how it works. Update variables like versions or haproxy build flags if needed.
List of HAProxy build flags:  
http://git.haproxy.org/?p=haproxy-1.6.git;a=blob_plain;f=Makefile;hb=HEAD

## Quick build on CentOS 7 x86_64
Install dependencies
```bash
yum -y install pcre-devel zlib-devel systemd-units wget tar git patch autoconf make automake libtool gcc-c++
```
Edit haproxy.spec for versions and build flags.  
```bash
sudo -i
cd /root

yum -y install rpmdevtools git

git clone https://github.com/DRN88/haproxy-libressl.git
cp -ra haproxy-libressl/centos7/rpmbuild /root/rpmbuild

spectool -g -R /root/rpmbuild/SPECS/haproxy.spec
rpmbuild -bb /root/rpmbuild/SPECS/haproxy.spec

```

## Artifacts
```bash
[root@rpmbuilder rpmbuild]# tree /root/rpmbuild/RPMS/
/root/rpmbuild/RPMS/
`-- x86_64
    |-- haproxy-1.6.6-1.el7.centos.x86_64.rpm
    `-- haproxy-debuginfo-1.6.6-1.el7.centos.x86_64.rpm

1 directory, 2 files
[root@rpmbuilder rpmbuild]#

```

## haproxy build flags check
```bash
[root@rpmbuilder7 ~]# haproxy -vvvv
HA-Proxy version 1.7.3 2017/02/28
Copyright 2000-2017 Willy Tarreau <willy@haproxy.org>

Build options :
  TARGET  = linux2628
  CPU     = generic
  CC      = gcc
  CFLAGS  = -m64 -march=x86-64 -O2 -g -fno-strict-aliasing -Wdeclaration-after-statement
  OPTIONS = USE_LINUX_SPLICE=1 USE_LINUX_TPROXY=1 USE_LIBCRYPT=1 USE_ZLIB=1 USE_REGPARM=1 USE_OPENSSL=1 USE_PCRE=1 USE_PCRE_JIT=1 USE_TFO=1

Default settings :
  maxconn = 2000, bufsize = 16384, maxrewrite = 1024, maxpollevents = 200

Encrypted password support via crypt(3): yes
Built with zlib version : 1.2.7
Running on zlib version : 1.2.7
Compression algorithms supported : identity("identity"), deflate("deflate"), raw-deflate("deflate"), gzip("gzip")
Built with OpenSSL version : LibreSSL 2.4.5
Running on OpenSSL version : LibreSSL 2.4.5
OpenSSL library supports TLS extensions : yes
OpenSSL library supports SNI : yes
OpenSSL library supports prefer-server-ciphers : yes
Built with PCRE version : 8.32 2012-11-30
Running on PCRE version : 8.32 2012-11-30
PCRE library supports JIT : yes
Built without Lua support
Built with transparent proxy support using: IP_TRANSPARENT IPV6_TRANSPARENT IP_FREEBIND

Available polling systems :
      epoll : pref=300,  test result OK
       poll : pref=200,  test result OK
     select : pref=150,  test result OK
Total: 3 (3 usable), will use epoll.

Available filters :
	[COMP] compression
	[TRACE] trace
	[SPOE] spoe

```

## Tips
If you are experimenting and do not want to wait for LibreSSL to recompile from scratch comment out ./autogen.sh.  
It will reuse the existing build.
