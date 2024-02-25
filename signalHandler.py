#!/usr/bin/env python3

import json
import logging
import subprocess
import sys


class SignalHandler:
    """Handle signal program - parse output, handle commands etc."""
    _signal_cmd = ['bin/signal-cli', '-o', 'json']

    def __init__(self, log_filename='signalHandler.log', log_level=logging.INFO):
        logging.basicConfig(filename=log_filename, encoding='utf-8', level=log_level)

    def receive_new_messages(self):
        """Receive new messages from server"""
        return self._parse_messages(self._call('receive'))

    def send_receipts(self, messages, type='read'):
        """Send receipt of given type for all given messages"""
        responses = []
        for m in messages:
            logging.debug(m)
            ac = m.get_source_account()
            ts = m.get_timestamp()
            responses.append(self._parse_receipt_response(
                self._call('sendReceipt', [ac, '-t', ts, '--type', type])
            ))

    def _call(self, command, extra_args=[]):
        """Call main program"""

        args = self._signal_cmd + [command] + extra_args
        logging.info(f'Call {args}')
        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            logging.error(f'signal-cli failed with RC={result.returncode}')
            logging.error(f'stderr: {result.stderr}')
            return

        logging.debug(f'result.stdout: {result.stdout}')
        return result.stdout.splitlines()

    def _parse_messages(self, output_lines):
        """Parse received messages and pack them into message class"""
        new_messages = []

        for ot in output_lines:
            line = ot.decode('utf-8')
            logging.info(f'Parse new message')
            logging.debug(f'message_str: {line}')
            j = json.loads(line)
            new_messages.append(SignalMessage(j))

        return new_messages

    def _parse_receipt_response(self, output_lines):
        """Parse send receipt response - if success or not"""
        receipts = []

        for ot in output_lines:
            line = ot.decode('utf-8')
            logging.info(f'Parse receipt response')
            logging.debug(f'response_str: {line}')
            j = json.loads(line)
            receipts.append(j['type'])

        return receipts


class SignalMessage():
    """Uncpacked single message"""
    _timestamp = ''
    _message_body = ''
    _source_account = ''
    _reaction = None
    _receipt_sent = False

    def __init__(self, message_data_in_json=None,
                 timestamp=None, source_account=None, message_body=None, reaction=None, receipt_sent=False):
        """Parse message data from json"""
        if message_data_in_json is not None:
            self._source_account = message_data_in_json['envelope']['source']
            md = message_data_in_json['envelope']['dataMessage']
            self._timestamp = md['timestamp']
            self._message_body = md['message']
            if 'reaction' in md:
                self._reaction = md['reaction']
        else:
            self._timestamp = timestamp
            self._source_account = source_account
            self._message_body = message_body
            self._reaction = reaction
        logging.debug(self)

    def __str__(self) -> str:
        return repr(f'SignalMessage ["source": {self._source_account}, "timestamp": {self._timestamp}, '
                    f'"body": {self._message_body}, "reaction": {self._reaction}]')

    def get_source_account(self) -> str:
        return self._source_account

    def get_timestamp(self) -> str:
        return str(self._timestamp)

    def get_sent_receipt(self) -> bool:
        return self._receipt_sent

    def mark_as_readed(self):
        """Send read receipt (if not done already) to sender"""
        self._receipt_sent = True


if __name__ == '__main__':
    # Simple test if called directly
    s = SignalHandler(log_filename=None, log_level=logging.DEBUG)
    logging.StreamHandler(sys.stderr)
    ms = s.receive_new_messages()
    print(s.send_receipts(ms))
