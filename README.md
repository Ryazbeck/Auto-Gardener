## Yarden Gnome Station (wip)


* [Purpose](#Purpose)
* [Goals](#goals)


## Purpose


#### portal:
##### Assist user with initial setup
1. Runs at boot
1. Listens for 3 second hold of button on station
    * This will take inputs to check status
    * Such as "tap" or various hold lengths
    * RGB LED will provide feedback
1. Turns up AP0
1. Configures wifi with user's input
1. Runs [nodogsplash](https://github.com/nodogsplash/nodogsplash)
1. Continues listening

#### sensors:
1. Retrieves its config stored on server
1. Reads sensor values
1. Stores sensor reads on server
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

