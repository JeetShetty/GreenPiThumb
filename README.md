# GreenPiThumb

[![Build
Status](https://travis-ci.org/JeetShetty/GreenPiThumb.svg?branch=master)](https://travis-ci.org/JeetShetty/GreenPiThumb)
[![Coverage
Status](https://coveralls.io/repos/JeetShetty/GreenPiThumb/badge.svg?branch=master&service=github)](https://coveralls.io/github/JeetShetty/GreenPiThumb?branch=master)

GreenPiThumb is a program that automatically waters a plant based on soil moisture levels, and records and displays the following:
- Ambient temperature
- Ambient humidity
- Ambient light
- Soil moisture level
- Photographs of the plant

## Installation

### Standard Installation

Run this on a Raspberry Pi device:

```bash
sudo apt-get update
sudo apt-get install build-essential python-dev
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
python setup.py install

cd ..
git clone https://github.com/JeetShetty/GreenPiThumb.git
cd GreenPiThumb
sudo pip install -r requirements.txt
cp greenpithumb/wiring_config.ini.example greenpithumb/wiring_config.ini
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
