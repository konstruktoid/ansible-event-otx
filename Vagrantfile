$ubuntu_script = <<-'UBUNTU'
apt-get update
apt-get --assume-yes upgrade
apt-get --assume-yes install build-essential maven openjdk-17-jdk python3-dev python3-pip

echo "
export JDK_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export JAVA_HOME=\$JDK_HOME
export PIP_NO_BINARY=jpy
export PATH=\$PATH:~/.local/bin
" >> /home/vagrant/.profile

echo "---
ungrouped:
  hosts:
    localhost:
      ansible_host: 127.0.0.1
  vars:
    ansible_connection: local" > /home/vagrant/inventory

chown vagrant:vagrant /home/vagrant/inventory

sudo -i -u vagrant pip3 install -U Jinja2
sudo -i -u vagrant pip3 install ansible ansible-rulebook ansible-runner OTXv2 wheel
UBUNTU

$fedora_script = <<-'FEDORA'
dnf --assumeyes upgrade
dnf --assumeyes install gcc java-17-openjdk maven python3-devel python3-pip

echo "
export JDK_HOME=/usr/lib/jvm/java-17-openjdk
export JAVA_HOME=\$JDK_HOME
export PIP_NO_BINARY=jpy
" >> /home/vagrant/.bashrc

echo "---
ungrouped:
  hosts:
    localhost:
      ansible_host: 127.0.0.1
  vars:
    ansible_connection: local" > /home/vagrant/inventory

chown vagrant:vagrant /home/vagrant/inventory

sudo -i -u vagrant pip3 install -U Jinja2
sudo -i -u vagrant pip3 install ansible ansible-rulebook ansible-runner OTXv2 wheel
FEDORA

Vagrant.configure("2") do |config|
  config.vbguest.installer_options = { allow_kernel_upgrade: true }
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
    v.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
    v.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
  end

  config.vm.define "ubuntu" do |ubuntu|
    ubuntu.ssh.extra_args = ["-o","ConnectTimeout=600"]
    ubuntu.ssh.insert_key = true
    ubuntu.vm.boot_timeout = 600
    ubuntu.vm.box = "ubuntu/jammy64"
    ubuntu.vm.hostname = "ubuntu"
    ubuntu.vm.provision "shell", inline: $ubuntu_script
  end

  config.vm.define "fedora" do |fedora|
    fedora.ssh.extra_args = ["-o","ConnectTimeout=600"]
    fedora.ssh.insert_key = true
    fedora.vm.boot_timeout = 600
    fedora.vm.box = "fedora/36-cloud-base"
    fedora.vm.hostname = "fedora"
    fedora.vm.provision "shell", inline: $fedora_script
  end
end
