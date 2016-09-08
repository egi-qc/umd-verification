#!/bin/bash -eu

set -x

# FIXME get it from somewhere
cat > /etc/httpd/conf/httpd.conf << EOF
ServerRoot "/etc/httpd"

PidFile logs/httpd.pid

Timeout                 300
KeepAlive               On
MaxKeepAliveRequests    100
KeepAliveTimeout        300

# (Replace /lib/ with /lib64/ if on x86_64!)
LoadModule log_config_module    /usr/lib64/httpd/modules/mod_log_config.so
LoadModule ssl_module           /usr/lib64/httpd/modules/mod_ssl.so
LoadModule gridsite_module      /usr/lib64/httpd/modules/mod_gridsite.so
LoadModule mime_module          /usr/lib64/httpd/modules/mod_mime.so
LoadModule dir_module           /usr/lib64/httpd/modules/mod_dir.so
LoadModule mpm_prefork_module           /usr/lib64/httpd/modules/mod_mpm_prefork.so
Include conf.modules.d/*.conf
TypesConfig /etc/mime.types

# User and group who will own files created by Apache
User  apache
Group apache

DocumentRoot "/var/www/html"

<Directory />
    AllowOverride None
</Directory>

LogLevel debug
LogFormat "%h \"%{SSL_CLIENT_S_DN}x\" %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined

CustomLog       logs/httpd-gridsite-access combined
ErrorLog        logs/httpd-gridsite-errors

HostnameLookups On

######################################################################
# Plain unauthenticated HTTP on ports 80 and 777
######################################################################
Listen 80
Listen 777
<VirtualHost *:80 *:777>
<Directory "/var/www/html">
 GridSiteIndexes	on
 GridSiteAuth		on
 GridSiteDNlists	/etc/grid-security/dn-lists/
</Directory>
</VirtualHost>

######################################################################
# Secured and possibly authenticated HTTPS on ports 443 and 488
######################################################################
Listen 443
Listen 488
SSLSessionCacheTimeout  300
#SSLSessionCache         shm:/var/cache/mod_ssl/shm_cache
SSLSessionCache         dbm:/var/cache/mod_ssl/scache

<VirtualHost *:443 *:488>
 
SSLEngine               on
SSLCertificateFile      /etc/grid-security/hostcert.pem
SSLCertificateKeyFile   /etc/grid-security/hostkey.pem
SSLCACertificatePath    /etc/grid-security/certificates
#SSLCARevocationPath    YOUR CRL DIRECTORY WOULD GO HERE
SSLVerifyClient         optional
SSLVerifyDepth          10
SSLOptions              +ExportCertData +StdEnvVars

<Directory "/var/www/html">
 GridSiteIndexes	on
 GridSiteAuth		on
 GridSiteDNlists	/etc/grid-security/dn-lists/
 GridSiteGSIProxyLimit	9
 GridSiteMethods	GET PUT DELETE MOVE
</Directory>
 
</VirtualHost>
EOF

[ ! -d /etc/grid-security/myproxy ] && mkdir -p /var/cache/mod_ssl

httpd
