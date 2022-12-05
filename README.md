# Dynamic firewall using Event Driven Ansible and AlienVault's OTX

```sh
vagrant up
git clone https://github.com/ansible/event-driven-ansible.git
cp otx.py event-driven-ansible/plugins/event_source/
cd event-driven-ansible || exit 1
ansible-galaxy collection install --force .
cp /vagrant/*.yml .
ansible-rulebook --verbose --inventory inventory --rulebook otx.yml
```
