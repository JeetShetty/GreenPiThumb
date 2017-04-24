# GreenPiThumb

[![Build
Status](https://travis-ci.org/JeetShetty/GreenPiThumb.svg?branch=master)](https://travis-ci.org/JeetShetty/GreenPiThumb)
[![Coverage
Status](https://coveralls.io/repos/JeetShetty/GreenPiThumb/badge.svg?branch=master&service=github)](https://coveralls.io/github/JeetShetty/GreenPiThumb?branch=master)

GreenPiThumb is a program that automatically waters a plant based on soil moisture levels, and records and displays the following:

* Ambient temperature
* Ambient humidity
* Ambient light
* Soil moisture level
* Photographs of the plant

## Installation

### Standard Installation

Run this on a Raspberry Pi device:

```bash
sudo apt-get update
sudo apt-get install build-essential python-dev python-picamera
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
python setup.py install

cd ..
git clone https://github.com/JeetShetty/GreenPiThumb.git
cd GreenPiThumb
sudo pip install -r requirements.txt
cp greenpithumb/wiring_config.ini.example greenpithumb/wiring_config.ini
```

#### Running GreenPiThumb

After running the above installation steps on your Pi, run GreenPiThumb with a command following the template below:

```bash
sudo python greenpithumb/greenpithumb.py \
  --poll_interval 15 \
  --photo_interval 240 \
  --sleep_window "23:15-07:00" \
  --sleep_window "14:30-15:45" \
  --image_path "images/" \
  --moisture_threshold 900
```

### Dev Installation

Run this on a system for development:

```bash
sudo apt-get update
sudo apt-get install build-essential python-dev
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install --force-test

cd ..
git clone https://github.com/JeetShetty/GreenPiThumb.git
cd GreenPiThumb
sudo pip install -r requirements.txt
sudo pip install -r dev_requirements.txt
cp greenpithumb/wiring_config.ini.example greenpithumb/wiring_config.ini
```

### Ansible Installation

This repository contains the GreenPiThumb backend, but GreenPiThumb also offers a [web frontend](https://github.com/JeetShetty/GreenPiThumb_Frontend_static) so you can check status of GreenPiThumb in your browser.

The instructions below explain how to install all backend and frontend components of GreenPiThumb to a Raspberry Pi device.

#### Local Self-Provision

If you're not familiar with Ansible, the simplest way to deploy GreenPiThumb is to install Ansible on the Pi itself and then use Ansible to self-provision the machine.

From a shell on the Raspberry Pi device itself, enter the following:

```bash
sudo apt-get update

# Install Ansible and dependencies
sudo apt-get install -y \
  libffi-dev \
  libyaml-dev \
  libpython2.7-dev \
  libssl-dev \
  python-pip \
  python2.7-dev
sudo pip install ansible paramiko PyYAML Jinja2 httplib2 six

# Install the Ansible GreenPiThumb role
sudo ansible-galaxy install JeetShetty.ansible-role-greenpithumb

# Create a minimal Ansible playbook to install GreenPiThumb
echo "- hosts: localhost
  roles:
    - { role: JeetShetty.ansible-role-greenpithumb }" > install.yml

# Self-provision for GreenPiThumb
sudo ansible-playbook install.yml
```

After this process completes, GreenPiThumb's backend and frontend will be running as services on the Pi. If you navigate to the Pi in a web browser (e.g. http://raspberrypi/ for a Pi named `raspberrypi`), you will see a dashboard similar to [greenpithumb.mtlynch.io](http://greenpithumb.mtlynch.io).

#### Remote Deployment

You can also use Ansible to deploy GreenPiThumb to a Raspberry Pi device from another Linux machine on the same network. You'll need to [install Ansible](http://docs.ansible.com/ansible/intro_installation.html) on your deployment machine (the non-Pi system).

Run the following commands on a Linux machine that has network access to your Pi device (e.g. on same local network):

```bash
PI_USER=pi                 # Change to the user on your Pi
PI_HOSTNAME=raspberrypi    # Change to your Pi's hostname.

# Install the Ansible GreenPiThumb role
sudo ansible-galaxy install JeetShetty.ansible-role-greenpithumb

# Create a minimal Ansible playbook to install GreenPiThumb
echo "- hosts: all
  roles:
    - { role: JeetShetty.ansible-role-greenpithumb}" > install.yml

# Provision the Pi using the playbook.
ansible-playbook install.yml \
  --user "${PI_USER}" \
  --ask-pass \
  --ask-sudo-pass \
  --become \
  --become-method sudo \
  -i "${PI_HOSTNAME},"
```

Ansible will prompt you for a password. Enter the password for the `PI_USER` account.

After this process completes, GreenPiThumb's backend and frontend will be running as services on the Pi. If you navigate to the Pi in a web browser (e.g. http://raspberrypi/ for a Pi named `raspberrypi`), you will see a dashboard similar to [greenpithumb.mtlynch.io](http://greenpithumb.mtlynch.io).

## Hardware

GreenPiThumb is designed for compatibility with a [Raspberry Pi device](https://www.raspberrypi.org/products/) running the [Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/).

An example wiring can be found below:

[![Fritzing wiring diagram](https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png)](https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png)

The Fritzing diagram file for this diagram is available in the [`doc` folder](doc/).

## Related Repositories

* [GreenPiThumb_Frontend](https://github.com/JeetShetty/GreenPiThumb_Frontend): Web API to provide status about GreenPiThumb.
* [GreenPiThumb_Frontend_static](https://github.com/JeetShetty/GreenPiThumb_Frontend_static): An AngularJS web app for viewing GreenPiThumb status (the static portion of the web frontend).
* [ansible-role-greenpithumb](https://github.com/JeetShetty/ansible-role-greenpithumb): An [Ansible](https://www.ansible.com/how-ansible-works) role for deploying all parts of GreenPiThumb to a system.
