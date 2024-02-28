#!/usr/bin/env python3
import logging

import config
import json
import requests
import sys

from jsonrpcclient import request, parse, Ok
from signalBot import SignalBot
from signalHandler import SignalRPCHandler


class SignalRPCBot(SignalBot):
    """Perform signalBot actions via jsonRPC endpoint rather than"""
    _log_filename = 'signalBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'

    def __init__(self, filename=_log_filename, encoding=_log_default_encoding, level=_log_default_level):
        """Init logging, signal handler etc."""
        logging.basicConfig(filename=filename, encoding=encoding, level=level)
        self._sh = SignalRPCHandler()

    def run(self):
        """Main loop of signalBot"""
        logging.info(f'BOT - Start listen for new messages at {config.SIGNALRPC_MESSAGE_STREAM_ENDPOINT}')
        r = requests.get(config.SIGNALRPC_MESSAGE_STREAM_ENDPOINT, stream=True)

        for line in r.iter_lines():
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line[:5] == 'data:':
                    logging.debug(f'BOT - Received new message: {decoded_line[5:]}')
                    for m in self._sh.parse_message(decoded_line[5:]):
                        self._process_message(m)


def main():
    sb = SignalRPCBot(level=logging.DEBUG)
    sb.run()
    print('hello there', file=sys.stderr)


if __name__ == '__main__':
    main()
