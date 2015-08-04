yum -y install wget

wget http://download.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm -O /tmp/epel-release-5-4.noarch.rpm
yum -y install /tmp/epel-release-5-4.noarch.rpm

yum -y install git
git clone https://github.com/egi-qc/umd-verification.git

yum -y install python26 python26-devel gcc python26-ldap

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python26 /tmp/get-pip.py
pip install Fabric
pip install -r umd-verification/requirements.txt
