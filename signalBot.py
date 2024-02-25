#!/usr/bin/env python3

import config
import logging
from signalHandler import SignalHandler



class SignalBot():
    """Check new messages in signal and perform some actions"""
    _sh = None
    _log_filename = 'signalBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'
    _receipt_type_view = 'view'
    _receipt_type_read = 'read'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(filename=filename, encoding=encoding, level=level)
        self._sh = SignalHandler()

    def run(self):
        """Main loop of signalBot"""
        for m in self._sh.receive_new_messages():
            self.process_message(m)

    def process_message(self, message):
        """Check what type of command is in the message and respond to it"""
        self._sh.send_receipts(message, receipt_type=self._receipt_type_view)
        body = message.get_message_body()
        logging.info(f'Process new message {message.get_timestamp()}')
        match body:
            case None:
                self.process_reaction(message)
            case _:
                logging.warning('Message type unknown')
                logging.debug(f'message_body: {message}')

    def process_reaction(self, message):
        """Process reaction to previous messages"""
        logging.info(f'Type of message: reaction')


def main():
    """Run bot instance"""
    sb = SignalBot()
    sb.run()


if __name__ == '__main__':
    main()
