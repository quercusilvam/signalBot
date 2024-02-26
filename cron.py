#!/usr/bin/env python3

from crontab import CronTab
import os

cron = CronTab(user=True)

path = os.path.abspath('./signalBot.py')
job = cron.new(command='python3 ' + "'" + path + "'")
job.minute.on(0)
job.hour.also.on(6)

cron.write()
