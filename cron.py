#!/usr/bin/env python3

from crontab import CronTab
import os

cron = CronTab(user=True)
path = os.path.abspath('./signalScheduledBot.py')

# Unread messages
job_um = cron.new(command='python3 ' + "'" + path + "--rpc --unread_messages'")
job_um.setall('30 6-21 * * *')

cron.write()
