## Yarden Gnome Station (wip)


* [Purpose](#Purpose)
* [Goals](#Goals)


## Purpose

#### button service:
##### Assists user with initial setup
1. Runs at boot
1. Listens for 3 second hold of button on station
    1. docker-compose run -d button (web server and python server)
        1. host files are bind volumes
        1. servers take user wifi info, configures pi, verifies connection, stops AP0, stops self
    1. Turns up AP0

#### sensor service:
##### Retrieves and stores sensor data
1. Runs at boot
1. If sensors then read
    1. If internet available
        1. Retrieve config from server
    1. If no internet
        1. Store local until internet available again
        1. push local to remote
1. If no sensors then report on portal that station has no sensors
1. Threshold logic is handled in Firebase Functions


## Goals

##### Hardware goals:
* Mobile first
* Waterproof
* Solar-powered
* Li-ion batteries
* Replaceable moisture sensors
* Solenoid valve (software controlled)
* Multi-functional button
* One-touch wifi setup (button)
* RGB LED for quick status (button)

##### Software goals:
* Captive portal (button) for wifi setup
* Cloud-based data and config
* Thresholds for controlling valve
* [Hypriot](https://github.com/hypriot/image-builder-rpi) for containerization

