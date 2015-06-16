yum -y install wget

wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm  -O /tmp/epel-release-6-8.noarch.rpm
yum -y install /tmp/epel-release-6-8.noarch.rpm

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

yum -y install python-ldap gcc python-devel

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python /tmp/get-pip.py

# Getting issues with upper versions
pip install Fabric==1.8.1
pip install PyYAML
