from gpiozero import Button
from subprocess import check_call
from signal import pause

def run_splash():
    print("Starting splash page...")
    check_call(['ifup', 'ap0'])
    check_call(['nodogsplash', '&'])

button = Button(24, hold_time=3, pull_up=False)
button.when_held = run_splash

pause()