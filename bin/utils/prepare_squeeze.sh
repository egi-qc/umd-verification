apt-get install git
git clone https://github.com/egi-qc/umd-verification.git

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python /tmp/get-pip.py

apt-get install gcc python-dev python-ldap
pip install Fabric
pip install PyYAML
