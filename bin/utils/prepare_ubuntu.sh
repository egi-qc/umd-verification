apt-get -y install git
git clone https://github.com/egi-qc/umd-verification.git

apt-get -y install gcc python-pip python-dev python-ldap python-pip
pip install Fabric
pip install -r umd-verification/requirements.txt
