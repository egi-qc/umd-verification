yum -y install wget

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

cat <<EOF >> /etc/yum.repos.d/puias-computational.repo
[PUIAS_6_computational]
name=PUIAS computational Base  \$releasever - \$basearch
mirrorlist=http://puias.math.ias.edu/data/puias/computational/\$releasever/\$basearch/mirrorlist
#baseurl=http://puias.math.ias.edu/data/puias/computational/\$releasever/\$basearch
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-puias
EOF

wget -q http://springdale.math.ias.edu/data/puias/6/x86_64/os/RPM-GPG-KEY-puias -O /etc/pki/rpm-gpg/RPM-GPG-KEY-puias
rpm --import RPM-GPG-KEY-puias

yum -y install gcc python27 python27-devel openldap-devel libffi-devel openssl-devel

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python2.7 /tmp/get-pip.py

# Getting issues with upper versions
pip2.7 install Fabric python-ldap
pip2.7 install -r umd-verification/requirements.txt
