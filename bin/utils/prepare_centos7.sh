yum -y install wget

wget http://mirror.uv.es/mirror/fedora-epel//epel-release-latest-7.noarch.rpm -O /tmp/epel-release-latest-7.noarch.rpm
yum -y install /tmp/epel-release-latest-7.noarch.rpm 

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

yum -y install python-pip

yum -y install gcc python-devel python-ldap
pip install fabric
pip install -r umd-verification/requirements.txt

pip uninstall
yum -y install python2-crypto
