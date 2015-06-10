yum -y install wget

wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm  -O /tmp/epel-release-6-8.noarch.rpm
yum -y install /tmp/epel-release-6-8.noarch.rpm

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

yum -y install python-pip python-ldap gcc python-devel

pip install Fabric
pip install PyYAML
