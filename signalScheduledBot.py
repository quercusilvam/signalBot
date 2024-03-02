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
        logging.basicConfig(filename=filename, encoding=encoding, level=level)
        self._sh = SignalHandler()

    def librus_check_new_messages(self):
        try:
            with LibrusHandler(config.LIBRUS_USERNAME, config.LIBRUS_PASSWORD) as lh:
                messages = lh.get_new_message()
                if messages is not None and len(messages) > 0:
                    mn = len(messages)
                    logging.info(f'SignalScheduledBot - Found {mn} messages')
                    message_body = f'{mn} new message(s) in account {config.LIBRUS_USERNAME}:\n\n'
                    for i in range(0, mn):
                        message_body += f'{i+1}. {messages[i]["sender"]}: {messages[i]["topic"]}\n\n'

                    for s in config.LIBRUS_SUBSCRIBERS:
                        self._sh.send_message(s, message_body)
                else:
                    logging.info('SignalScheduledBot - No new messages')
        except RuntimeError as re:
            logging.error(f'SignalScheduledBot - Cannot check new messages for account {config.LIBRUS_USERNAME}')
            logging.error(f'SignalScheduledBot - exception: {re}')


class SignalScheduledRPCBot(SignalScheduledBot):
    """Version of SignalScheduledBot that handle jsonRPC protocol"""
    _log_filename = 'signalScheduledRPCBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(filename=filename, encoding=encoding, level=level)
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

    args = parser.parse_args()
    is_rpc = args.rpc

    if is_rpc:
        s = SignalScheduledRPCBot(level=logging.DEBUG)
        s.librus_check_new_messages()
    else:
        s = SignalScheduledBot(level=logging.DEBUG)
        s.librus_check_new_messages()


if __name__ == '__main__':
    main()
