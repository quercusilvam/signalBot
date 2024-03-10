#!/usr/bin/env python3

import config
import common

import argparse
import logging
import sys

from librusHandler import LibrusHandler
from signalHandler import SignalHandler, SignalRPCHandler


class SignalScheduledBot:
    """Handle all scheduler actions, like periodically checking some sites etc."""
    _sh = None
    _log_filename = 'signalScheduledBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=filename,
                            encoding=encoding,
                            level=level)
        self._sh = SignalHandler()

    def librus_check_new_messages(self):
        """Check for unread messages in librusSynergia page"""
        accounts = config.LIBRUS_USERS
        for ac in accounts:
            ac_name = ac['account']
            ac_user = ac['username']
            ac_pass = ac['password']
            try:
                logging.info(f'SignalScheduledBot - checking unread messages for {ac_name}')
                with LibrusHandler(ac_user, ac_pass) as lh:
                    messages = lh.get_unread_messages()
                    if messages is not None and len(messages) > 0:
                        self._send_unread_messages_to_librus_subscribers(messages, ac_name)
                    else:
                        logging.info(f'SignalScheduledBot - No new messages for account {ac_name}')
            except RuntimeError as re:
                logging.error(f'SignalScheduledBot - Cannot check new messages for account {ac_name}', exc_info=True)
                self._send_error_message(f'SignalScheduledBot - Cannot check new messages for account {ac_name}',
                                         attachments=[lh.get_error_screenshot()])
                self._send_message_to_librus_subscribers(f'Cannot check new messages for account {ac_name}\n'
                                                         'Please do it manually')

    def librus_get_schedule(self, next_week=False):
        """Get schedule for given accounts. This week (default) lub next one"""
        accounts = config.LIBRUS_USERS
        for ac in accounts:
            ac_name = ac['account']
            ac_user = ac['username']
            ac_pass = ac['password']
            try:
                logging.info(f'SignalScheduledBot - get schedule for {ac_name}')
                with LibrusHandler(ac_user, ac_pass) as lh:
                    message_body = f'Schedule for {ac_name}'
                    if next_week:
                        message_body += ' for next week'
                    schedule_file = lh.get_schedule(next_week=next_week)
                    self._send_message_to_librus_subscribers(message_body, attachments=[schedule_file])
            except RuntimeError:
                logging.error(f'SignalScheduledBot - Cannot check schedule for account {ac_name}', exc_info=True)
                self._send_error_message(f'SignalScheduledBot - Cannot check schedule for account {ac_name}',
                                         attachments=[lh.get_error_screenshot()])
                self._send_message_to_librus_subscribers(f'Cannot check schedule for account {ac_name}\n'
                                                         'Please do it manually')

    def _send_unread_messages_to_librus_subscribers(self, messages, account):
        """Send unread messages to subscribers"""
        mn = len(messages)
        logging.info(f'SignalScheduledBot - Found {mn} messages')
        for i in range(0, mn):
            message_body = f'New message in account {account}:\n\n'
            message_body += f'{i + 1}. {messages[i]["sender"]}: {messages[i]["topic"]}\n\n{messages[i]["body"]}'
            self._send_message_to_librus_subscribers(message_body)

    def _send_message_to_librus_subscribers(self, message_body, attachments=[]):
        for s in config.LIBRUS_SUBSCRIBERS:
            self._sh.send_message(s, message_body, attachments=attachments)

    def _send_error_message(self, message_body, attachments=[]):
        """Send messages to admins about errors"""
        for a in config.SIGNAL_ADMINS:
            self._sh.send_message(a, message_body, attachments=attachments)


class SignalScheduledRPCBot(SignalScheduledBot):
    """Version of SignalScheduledBot that handle jsonRPC protocol"""
    _log_filename = 'signalScheduledRPCBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=filename,
                            encoding=encoding,
                            level=level)
        self._sh = SignalRPCHandler()


def main():
    """Run bot instance"""
    # sb = SignalBot(filename=None, level=logging.DEBUG)
    # logging.StreamHandler(sys.stderr)
    # sb.run()
    desc = '''Create signalScheduledBOT or signalScheduledRPCBOT instance that receive and handles messages from users

This BOT has two options:
signalScheduledBOT (default) - call each command by create subprocess of signal-cli tool. This is easier to
                               to handle but is slow
signalScheduledRPCBOT (use --rpc option to set) - uses HTTP jsonRPC endpoint to call signal-cli. Needs the
                                                  endpoint creation before you run the script in other thread.'''
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--rpc', action='store_true',
                        help='If set the signalScheduledRPCBOT version will be used (instead of signalBOT)')
    parser.add_argument('--unread_messages', action='store_true',
                        help='If set return unread messages for all accounts to all subscribers')
    parser.add_argument('--this_week_schedule', action='store_true',
                        help='If set return schedule for this week for all accounts to all subscribers')
    parser.add_argument('--next_week_schedule', action='store_true',
                        help='If set return schedule for next week for all accounts to all subscribers. '
                             'Useful in weekends')

    args = parser.parse_args()
    is_rpc = args.rpc
    get_unread_messages = args.unread_messages
    get_this_week_schedule = args.this_week_schedule
    get_next_week_schedule = args.next_week_schedule

    if is_rpc:
        s = SignalScheduledRPCBot(level=logging.INFO)
    else:
        s = SignalScheduledBot(level=logging.INFO)

    if get_unread_messages:
        s.librus_check_new_messages()
    if get_this_week_schedule:
        s.librus_get_schedule()
    if get_next_week_schedule:
        s.librus_get_schedule(next_week=True)


if __name__ == '__main__':
    main()
