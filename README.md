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

# SignalRPCBot
This tool connect to running instance of signal-cli in http mode.
You need to run it manually:

`signal-cli -a ACCOUNT daemon --http [HTTP] [--no-receive-stdout]`

For example:

`signal-cli -a +1122334455 daemon --http localhost --no-receive-stdout`

HTTP server will start and signal-cli will wait commands.

Then you run `signalRCPBot.py` (in another shell/thread) and this version of the bot
will try to connect to daemon and communicate via API. You need to update `config.py` file with
correct HTTP endpoint if you use different from localhost.

## Benefits
This work a way faster as signal-cli needs JVM starts and running without daemon ends with
starting JVM several times for one bot action and take a lot of resources.
With daemon and API it keeps JVM running all the time - which is faster (but uses more RAM)

# Dependencies
https://github.com/AsamK/signal-cli - main tool.

You need to download it and setup signal-cli itself. Copy /lib & /bin files into main directory of this project.

Tested on version 0.13.0

# License
Licensed under the GPLv3: http://www.gnu.org/licenses/gpl-3.0.html
