yum -y install wget

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

yum -y install python-pip

yum -y install gcc python-devel python-ldap
pip install fabric
pip install -r umd-verification/requirements.txt

pip uninstall
yum -y install python2-crypto
