#!/usr/bin/env python3
import sys

import config
import logging
import re

from signalHandler import SignalHandler



class SignalBot():
    """Check new messages in signal and perform some actions"""
    _sh = None
    _log_filename = 'signalBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'
    _emoji_unknown = '❓'
    _emoji_ok = '👍'

    _pattern_yt = r'(https?://)?(www\.)?(m\.)?(youtube\.com|youtu\.be)/.*'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(filename=filename, encoding=encoding, level=level)
        self._sh = SignalHandler()

    def run(self):
        """Main loop of signalBot"""
        for m in self._sh.receive_new_messages():
            self._process_message(m)

    def _process_message(self, message):
        """Check what type of command is in the message and respond to it"""
        self._sh.send_receipt(message)

        body = message.get_message_body()
        logging.info(f'Process new message {message.get_timestamp()}')
        if body is None:
            logging.info('No body message. Looking for other message types')
            logging.warning('Not implemented yet!')
        elif not self._find_known_message_body_pattern(body):
            logging.warning('Message type unknown')
            logging.debug(f'message_body: {message}')

    def _find_known_message_body_pattern(self, message_body):
        """Use regexp to find known message instruction"""
        if re.search(self._pattern_yt, message_body) is not None:
            self._process_yt_message(message_body)
            return True
        return False

    def _process_yt_message(self, message_body):
        """Download given YouTube as mp3 or mp4"""
        logging.info('Found YouTube message. Download file')
        logging.warning('Not implemented yet!')

    def _process_reaction(self, message):
        """Process reaction to previous messages"""
        logging.info(f'Type of message: reaction')


def main():
    """Run bot instance"""
    sb = SignalBot(filename=None, level=logging.DEBUG)
    logging.StreamHandler(sys.stderr)
    sb.run()


if __name__ == '__main__':
    main()
