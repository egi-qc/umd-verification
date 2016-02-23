apt-get -y install git
git clone https://github.com/egi-qc/umd-verification.git

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python /tmp/get-pip.py

apt-get install -y gcc python-dev python-ldap
pip install Fabric
pip install -r umd-verification/requirements.txt
