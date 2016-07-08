#!/bin/bash

yum -y install wget tar git patch autoconf make automake libtool gcc-c++ zlib-devel


cd /tmp
wget "https://github.com/libressl-portable/portable/archive/v2.3.6.tar.gz"
tar -xzf v2.3.6.tar.gz
cd /tmp/portable-2.3.6
./autogen.sh
./configure --prefix=/tmp/static-libressl-2.3.6 --enable-shared=no --enable-static=yes
make
make install


# PCRE Build
cd /tmp
wget "http://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.39.tar.gz"
tar -xzf pcre-8.39.tar.gz
./configure --prefix=/tmp/static-pcre-8.39 --enable-shared=no --enable-utf8 --enable-jit
make
make install


# Building RPM too
yum -y install rpmdevtools

rpmdev-setuptree


/root/rpmbuild/BUILDROOT/haproxy-1.6.6-1.el7.centos.x86_64/usr/sbin/haproxy-systemd-wrapper
