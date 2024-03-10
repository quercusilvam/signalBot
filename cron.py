#!/usr/bin/env python3

import argparse
import os

from crontab import CronTab


def main():
    """Add info to crontab"""
    desc = '''Create crontab entries for signalBot'''
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--rpc', action='store_true',
                        help='If set the signalRPCBOT version will be used (instead of signalBOT)')

    args = parser.parse_args()
    is_rpc = args.rpc

    cron = CronTab(user=True)

    if is_rpc:
        path = os.path.abspath('./signalScheduledBot.py')

        # Unread messages
        job_um = cron.new(command='python3 ' + "'" + path + "' --rpc --unread_messages")
        job_um.setall('15,45 6-20 * * *')

        # Schedule
        job_schedule_morning = cron.new(command='python3 ' + "'" + path + "' --rpc --this_week_schedule")
        job_schedule_morning.setall('0 8 * * MON-FRI')
        job_schedule_afternoon = cron.new(command='python3 ' + "'" + path + "' --rpc --this_week_schedule")
        job_schedule_afternoon.setall('30 19 * * MON-THU')
        job_schedule_sunday = cron.new(command='python3 ' + "'" + path + "' --rpc --next_week_schedule")
        job_schedule_sunday.setall('30 19 * * SUN')

        cron.write()
    else:
        path = os.path.abspath('./signalScheduledBot.py')

        # Unread messages
        job_um = cron.new(command='python3 ' + "'" + path + "' --unread_messages")
        job_um.setall('30 6-20 * * *')

        cron.write()


if __name__ == '__main__':
    main()
