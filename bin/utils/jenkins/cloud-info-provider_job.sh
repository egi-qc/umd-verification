#DEBIAN_FRONTEND=noninteractive sudo apt-get -qqy update || sudo yum update -qy
#DEBIAN_FRONTEND=noninteractive sudo apt-get install -qqy git || sudo yum install -qy git
#
#git clone https://git.openstack.org/openstack-dev/devstack -b stable/${OpenStack_release} 
#sudo ./devstack/tools/create-stack-user.sh
#sudo usermod -a -G sudo stack
#sudo mv devstack /opt/devstack
#sudo su - stack
#sudo chown -R stack:stack /opt/devstack
#
#cd /opt/devstack
#ls -l
#
#cat <<EOF > local.conf
#[[local|localrc]]
#ADMIN_PASSWORD=secret
#DATABASE_PASSWORD=secret
#RABBIT_PASSWORD=secret
#SERVICE_PASSWORD=secret
#disable_service n-net
#enable_service q-svc
#enable_service q-agt
#enable_service q-dhcp
#enable_service q-l3
#enable_service q-meta
#IP_VERSION=4
#NEUTRON_CREATE_INITIAL_NETWORKS=False
#FLOATING_RANGE=192.168.1.224/27
#FIXED_RANGE=10.11.12.0/24
#FIXED_NETWORK_SIZE=256
#FLAT_INTERFACE=eth0
#EOF

#cd ~/devstack
#FORCE=yes ./stack.sh
#source openrc
#nova flavor-list

# Ansible 2.2
sudo pip install ansible==2.2
if [ ! -d /tmp/ansible-role-cloud-info-provider ]; then
    git clone https://github.com/egi-qc/ansible-role-cloud-info-provider -b umd /tmp/ansible-role-cloud-info-provider
fi
sudo ansible-galaxy install -r /tmp/ansible-role-cloud-info-provider/requirements.yml

cd "$WORKSPACE"
Verification_repository=$(./bin/jenkins/parse_repos.sh ${Verification_repository})

fab cloud-info-provider:cmd_release=${CMD_OS_release},openstack_release=${OpenStack_release},${Verification_repository},log_path=logs
