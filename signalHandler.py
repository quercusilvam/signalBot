#!/usr/bin/env python3

import common
import config

import json
import logging
import requests
import subprocess
import sys

from jsonrpcclient import request, parse, Ok


class SignalHandler:
    """Handle signal program - parse output, handle commands etc."""
    _default_encoding = 'utf8'
    _signal_cmd = [config.SIGNAL_CMD_PATH, '-o', 'json']
    _cmd_receive = 'receive'
    _cmd_send_receipt = 'sendReceipt'
    _cmd_send_receipt_param_timestamp = '-t'
    _cmd_send_receipt_param_type = '--type'
    _cmd_send_receipt_default_type = 'read'
    _cmd_send_reaction = 'sendReaction'
    _cmd_send_reaction_param_author = '-a'
    _cmd_send_reaction_param_timestamp = '-t'
    _cmd_send_reaction_param_emoji = '-e'
    _cmd_send_reaction_emoji_ok = '👍'
    _cmd_send_message = 'send'
    _cmd_send_message_param_message = '-m'
    _cmd_send_message_param_quote_timestamp = '--quote-timestamp'
    _cmd_send_message_param_quote_author = '--quote-author'

    def receive_new_messages(self):
        """Receive new messages from server"""
        return self._parse_messages(self._call(self._cmd_receive))

    def send_receipts(self, messages, receipt_type=_cmd_send_receipt_default_type):
        """Send receipt of given type for all given messages"""
        responses = []
        for m in messages:
            responses.append(self.send_receipt(m, receipt_type))
        return responses

    def send_receipt(self, message, receipt_type=_cmd_send_receipt_default_type):
        """Send receipt of given type for one message"""
        logging.debug(f'send_receipt.message: {message}')
        ac = message.get_source_account()
        ts = message.get_timestamp()
        return self._parse_receipt_response(
            self._call(self._cmd_send_receipt, [
                ac, self._cmd_send_receipt_param_timestamp, ts, self._cmd_send_receipt_param_type, receipt_type
            ])
        )

    def send_reactions(self, messages, emoji=_cmd_send_reaction_emoji_ok):
        """Send reaction for all given messages"""
        responses = []
        for m in messages:
            responses.append(self.send_reaction(m, emoji))
        return responses

    def send_reaction(self, message, emoji=_cmd_send_reaction_emoji_ok):
        """Send reaction for message"""
        logging.debug(f'send_reaction.message: {message}')
        logging.debug(f'send_reaction.emoji: {emoji}')
        ac = message.get_source_account()
        ts = message.get_timestamp()
        return self._parse_receipt_response(
            self._call(self._cmd_send_reaction, [
                ac,
                self._cmd_send_reaction_param_author,
                ac,
                self._cmd_send_reaction_param_timestamp,
                ts,
                self._cmd_send_reaction_param_emoji,
                emoji
            ])
        )

    def send_message(self, recipient, message_body, quote_timestamp=None):
        """Send a message to another user"""
        logging.debug(f'send_message.recipient: {recipient}')
        logging.debug(f'send_message.message_body: {message_body}')
        if quote_timestamp is None:
            return self._parse_receipt_response(
                self._call(self._cmd_send_message, [
                    recipient, self._cmd_send_message_param_message, message_body
                ])
            )
        else:
            logging.debug(f'send_message.quote_timestamp: {quote_timestamp}')
            return self._parse_receipt_response(
                self._call(self._cmd_send_message, [
                    recipient,
                    self._cmd_send_message_param_message,
                    message_body,
                    self._cmd_send_message_param_quote_timestamp,
                    quote_timestamp,
                    self._cmd_send_message_param_quote_author,
                    recipient
                ])
            )

    def _call(self, command, extra_args=[]):
        """Call main program"""

        for i in range(0, len(extra_args)):
            extra_args[i] = str(extra_args[i])
        args = self._signal_cmd + [command] + extra_args
        logging.info(f'Call {args}')
        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            logging.error(f'signal-cli failed with RC={result.returncode}')
            logging.error(f'stderr: {result.stderr}')
            raise RuntimeError('Run signal-cli failed')

        logging.debug(f'result.stdout: {result.stdout}')
        return result.stdout.splitlines()

    def _parse_messages(self, output_lines, decoded=False):
        """Parse received messages and pack them into message class"""
        new_messages = []

        for ot in output_lines:
            if decoded:
                line = ot
            else:
                line = ot.decode(self._default_encoding)
            logging.info(f'Parse new message')
            logging.debug(f'_parse_messages.message_str: {line}')
            j = json.loads(line)
            if 'receiptMessage' in j['envelope']:
                logging.info('This is receiptMessage. Ignoring')
            elif 'syncMessage' in j['envelope']:
                logging.info('This is syncMessage. Ignoring')
            elif 'typingMessage' in j['envelope']:
                logging.info('This is typingMessage. Ignoring')
            elif 'dataMessage' in j['envelope']:
                new_messages.append(SignalMessage(j))
            else:
                logging.warning('Message type unknown')

        return new_messages

    def _parse_receipt_response(self, output_lines, decoded=False):
        """Parse send receipt response - if success or not"""
        receipts = []

        for ot in output_lines:
            if decoded:
                line = ot
            else:
                line = ot.decode(self._default_encoding)
            logging.info(f'Parse receipt response')
            logging.debug(f'response_str: {line}')
            j = json.loads(line)
            receipts.append(j['results'][0]['type'])

        return receipts


class SignalRPCHandler(SignalHandler):
    """Perform calls via jsonRCP endpoint; not directly"""
    _cmd_send_receipt_param_recipient = 'recipient'
    _cmd_send_receipt_param_timestamp = 'targetTimestamp'
    _cmd_send_receipt_param_type = 'type'
    _cmd_send_receipt_default_type = 'read'
    _cmd_send_reaction_param_recipient = 'recipient'
    _cmd_send_reaction_param_author = 'targetAuthor'
    _cmd_send_reaction_param_timestamp = 'targetTimestamp'
    _cmd_send_reaction_param_emoji = 'emoji'
    _cmd_send_message_param_recipient = 'recipient'
    _cmd_send_message_param_message = 'message'
    _cmd_send_message_param_quote_timestamp = 'quoteTimestamp'
    _cmd_send_message_param_quote_author = 'quoteAuthor'

    def receive_new_messages(self):
        """For RPC this is not implemented"""
        logging.warning('This function should not be called for signalRPCHandler')

    def parse_message(self, output_line):
        return self._parse_messages([output_line], True)

    def _call(self, command, extra_args=[]):
        """Send jsonRPC request to signalcli endpoint

            Note: You cannot receive things this way (there is different endpoint that stream received things)
            Function will return Exception if you try
        """

        # Add specific keywords needed by jsonRPC
        match command:
            case self._cmd_receive:
                raise RuntimeError(f'Cannot call {self._cmd_receive} in SignalRCPHandler')
            case self._cmd_send_receipt:
                logging.debug(f'Adding {self._cmd_send_receipt_param_recipient} keyword for {command}')
                extra_args = [self._cmd_send_receipt_param_recipient] + extra_args
            case self._cmd_send_reaction:
                logging.debug(f'Adding {self._cmd_send_reaction_param_recipient} keyword for {command}')
                extra_args = [self._cmd_send_reaction_param_recipient] + extra_args
            case self._cmd_send_message:
                logging.debug(f'Adding {self._cmd_send_message_param_recipient} keyword for {command}')
                extra_args = [self._cmd_send_message_param_recipient] + extra_args
            case _:
                logging.debug(f'Command {command} does not need anny additional keywords')

        params = common.convert_list_to_dict(extra_args)
        logging.info(f'Call {command} with params {params} on {config.SIGNALRPC_POST_ENDPOINT}')

        response = requests.post(config.SIGNALRPC_POST_ENDPOINT, json=request(command, params))
        parsed = parse(response.json())
        if isinstance(parsed, Ok):
            logging.debug(f'Call OK. Response: {parsed.result}')
            return [parsed.result]
        else:
            logging.error(f'Access API {command} failed: {parsed.message}')
            raise RuntimeError(f'Access API {command} failed: {parsed.message}')


class SignalMessage:
    """Unpacked single message"""
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
        return self._timestamp

    def get_message_body(self):
        return self._message_body

    def get_sent_receipt(self) -> bool:
        return self._receipt_sent

    def mark_as_readed(self):
        """Send read receipt (if not done already) to sender"""
        self._receipt_sent = True


if __name__ == '__main__':
    # Simple test if called directly
    s = SignalHandler()
    logging.StreamHandler(sys.stderr)
    ms = s.receive_new_messages()
    print(s.send_receipts(ms))
