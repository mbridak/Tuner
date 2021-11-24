# Tuner
[![License: GPL v3](https://img.shields.io/github/license/mbridak/Tuner)](https://opensource.org/licenses/MIT)  [![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)  [![Made With:PyQt5](https://img.shields.io/badge/Made%20with-PyQt5-red)](https://pypi.org/project/PyQt5/)



This is a scratch my own itch project. I use [potato](https://github.com/mbridak/potato) for [POTA](https://pota.app/#/) hunting, and [sotacracker](https://github.com/mbridak/sotacracker) for chasing [SOTA](https://www.sota.org.uk/).
So when I click on an activation in one of those apps, my radio will be changed to a new band, and on the spotted frequency using [rigctld](https://manpages.ubuntu.com/manpages/precise/man8/rigctld.8.html).

One does not want to tune up on top of an activator. So I made this little app. What it does is remembers what frequency and mode you are on.
Then tunes the radio away to a fairly safe frequency. Which just coincidentally happens to be the start of the FT8 window for that band:fire:. No one uses that anyways...
Switches your mode to CW so you can key down to initiate a tune cycle, or press the tune button on your rig/tuner.
Once the cycle is complete, you press the tune button again, and the radio is changed back to the original frequency and mode you started on:beers:.

## Running from source

Install Python 3, then two required libraries.

If you're the Ubuntu/Debian type you can:

`sudo apt install python3-pyqt5 python3-requests`

You can install libraries via pip:

`python3 -m pip3 install -r requirements.txt`

Just make tuner.py executable and run it within the same folder, or type:

`python3 tuner.py`

