# signal BOT
A tool in Python3 that handles some messages in signal communicator and return some responses.

You should have a server you can run this tool in loop.

Main elements:
## signalBot
Main program where you can define processes that will happen according to different
messages types/reactions/others that you will receive

## signalcliHandler
Helper class that allows handling signal-cli Java tool in Python.

## cron.py
Helper file that setup crontab command to start bot every morning

# Dependencies
https://github.com/AsamK/signal-cli - main tool.

You need to download it and setup signal-cli itself. Copy /lib & /bin files into main directory of this project.

Tested on version 0.13.0

# License
Licensed under the GPLv3: http://www.gnu.org/licenses/gpl-3.0.html
