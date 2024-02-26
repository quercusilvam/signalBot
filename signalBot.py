#!/usr/bin/env python3
import sys

import config
import logging
import os
import re
import time
import urllib
import uuid


from pytube import YouTube
from signalHandler import SignalHandler



class SignalBot():
    """Check new messages in signal and perform some actions"""
    _sh = None
    _log_filename = 'signalBot.log'
    _log_default_level = logging.INFO
    _log_default_encoding = 'utf8'
    _emoji_unknown = '❓'
    _emoji_ok = '👍'

    _pattern_ping = r'(ping)'
    _pattern_yt = r'(https?://)?(www\.)?(m\.)?(youtube\.com|youtu\.be)/.*'
    _pytube_audio_tag = 140
    _pytube_file_extension = '.mp4'

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
        logging.info(f'BOT - trying to process message {message.get_timestamp()}')
        if body is None:
            logging.info('BOT - No body message. Looking for other message types')
            logging.warning('Not implemented yet!')
        elif self._find_known_message_body_pattern(message):
            self._sh.send_reaction(message, self._emoji_ok)
        else:
            logging.warning('BOT - Message type unknown')
            logging.debug(f'message_body: {message}')
            self._sh.send_reaction(message, self._emoji_unknown)

    def _find_known_message_body_pattern(self, message):
        """Use regexp to find known message instruction"""
        body = message.get_message_body()

        if re.fullmatch(self._pattern_ping, body, re.IGNORECASE) is not None:
            self._process_ping_message(message)
            return True
        if re.search(self._pattern_yt, body) is not None:
            self._process_yt_message(message)
            return True
        return False

    def _process_ping_message(self, message):
        """Return simple pong"""
        logging.info('BOT - Found PING message. Responding PONG')
        self._sh.send_message(message.get_source_account(), 'pong', message.get_timestamp())

    def _process_yt_message(self, message):
        """Download given YouTube as mp3 or mp4"""
        logging.info('BOT - Found YouTube message. Download file')
        dirname = str(uuid.uuid4())
        os_path = os.path.join(config.HTTP_YT_LOCATION, dirname)
        os.mkdir(os_path)
        yt = YouTube(message.get_message_body())
        filename = yt.title[:48] + self._pytube_file_extension
        filename = re.sub(' ', '_', filename)
        stream = yt.streams.get_by_itag(self._pytube_audio_tag)
        final_file = stream.download(output_path=os_path, filename=filename)
        logging.info(f'BOT - File downloaded as {final_file}')
        parsed_filename = urllib.parse.quote_plus(filename)
        self._sh.send_message(message.get_source_account(), f'{config.YT_SERVER_PREFIX}{dirname}/{parsed_filename}', message.get_timestamp())


    def _process_reaction(self, message):
        """Process reaction to previous messages"""
        logging.info(f'BOT - Found reaction')
        logging.warning('Not implemented yet!')


def main():
    """Run bot instance"""
    # sb = SignalBot(filename=None, level=logging.DEBUG)
    # logging.StreamHandler(sys.stderr)
    # sb.run()
    sb = SignalBot(level=logging.DEBUG)
    while True:
        sb.run()
        time.sleep(60)


if __name__ == '__main__':
    main()
