# Dynamic firewall using Event Driven Ansible and AlienVault's OTX

This is a example of how to use [ansible-rulebook](https://github.com/ansible/ansible-rulebook/)
to dynamically update a firewall blocklist using
[AlienVault's Open Threat Exchange (OTX)](https://otx.alienvault.com/) as an
event source.

## Quickstart

If you prefer working with Fedora, replace `ubuntu` with `fedora` in the code
block below.

```sh
vagrant up ubuntu
vagrant ssh ubuntu
git clone https://github.com/ansible/event-driven-ansible.git
cd event-driven-ansible || exit 1
ansible-galaxy collection install --force .
cd .. || exit 1
export OTX_APIKEY="YOUR_OTX_APIKEY"
cp /vagrant/*.yml .
ansible-rulebook --inventory inventory --rulebook otx.yml --source-dir /vagrant/
```

## Structure

```console
.
├── otx.py
├── otx.yml
└── otx_ufw.yml
```

### Event source - `otx.py`

Stream subscribed OTX events.

#### Arguments

##### count

Minimum count of related pulses that is required for the
IP to be added to the blocklist.

### Rulebook - `otx.yml`

```yml
- name: otx events
  hosts: all
  sources:
    - name: Match all messages
      ansible.eda.otx:
        count: "1"
  rules:
    - name: Send to playboox
      condition: event.otx is defined
      action:
        run_playbook:
          name: otx_ufw.yml
```

### Playbook - `otx_ufw.yml`

```yml
- name: otx events
  hosts: all
  tasks:
    - name: Deny OTX indicator address
      become: true
      community.general.ufw:
        rule: deny
        src: '{{ event.otx.ip }}'
        comment: "ansible managed - OTX indicator"
```
