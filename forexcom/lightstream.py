#  Copyright (c) Lightstreamer Srl.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file has been modified by Ali Zahedigol.

import logging
import threading
import traceback
from functools import partial

from forexcom.utils import send_request

CONNECTION_URL_PATH = "lightstreamer/create_session.txt"
BIND_URL_PATH = "lightstreamer/bind_session.txt"
CONTROL_URL_PATH = "lightstreamer/control.txt"
# Request parameter to create and activate a new Table.
OP_ADD = "add"
# Request parameter to delete a previously created Table.
OP_DELETE = "delete"
# Request parameter to force closure of an existing session.
OP_DESTROY = "destroy"
# List of possible server responses
PROBE_CMD = "PROBE"
END_CMD = "END"
LOOP_CMD = "LOOP"
ERROR_CMD = "ERROR"
SYNC_ERROR_CMD = "SYNC ERROR"
OK_CMD = "OK"

log = logging.getLogger()


class StreamerSubscription(object):
    """Represents a Subscription to be submitted to a Lightstreamer Server."""

    def __init__(self, mode, items, fields, adapter=""):
        self.item_names = items
        self._items_map = {}
        self.field_names = fields
        self.adapter = adapter
        self.mode = mode
        self.snapshot = "true"
        self._listeners = []

    def _decode(self, value, last):
        """Decode the field value according to
        Lightstreamer Text Protocol specifications.
        """
        if value == "$":
            return u''
        elif value == "#":
            return None
        elif not value:
            return last
        elif value[0] in "#$":
            value = value[1:]

        return value

    def addlistener(self, listener):
        self._listeners.append(listener)

    def notifyupdate(self, item_line):
        """Invoked by LSClient each time Lightstreamer Server pushes
        a new item event.
        """
        # Tokenize the item line as sent by Lightstreamer
        toks = item_line.rstrip('\r\n').split('|')
        undecoded_item = dict(list(zip(self.field_names, toks[1:])))

        # Retrieve the previous item stored into the map, if present.
        # Otherwise create a new empty dict.
        item_pos = int(toks[0])
        curr_item = self._items_map.get(item_pos, {})
        # Update the map with new values, merging with the
        # previous ones if any.
        self._items_map[item_pos] = dict(
            [(k, self._decode(v, curr_item.get(k))) for k, v in list(undecoded_item.items())],
        )
        # Make an item info as a new event to be passed to listeners
        item_info = {
            'pos': item_pos,
            'name': self.item_names[item_pos - 1],
            'values': self._items_map[item_pos],
        }

        # Update each registered listener with new event
        for on_item_update in self._listeners:
            on_item_update(item_info)


class StreamerClient(object):
    """Manages the communication with Lightstreamer Server"""

    def __init__(self, base_url=None, adapter_set=""):
        if not base_url:
            base_url = 'https://push.cityindex.com/'
        self._base_url = base_url
        self._call = partial(send_request, 'POST', stream=True)
        self._adapter_set = adapter_set
        self._username = None
        self._password = None
        self._session = {}
        self._subscriptions = {}
        self._current_subscription_key = 0
        self._stream_connection = None
        self._stream_connection_thread = None
        self._bind_counter = 0

    def _set_control_link_url(self, custom_address=None):
        """Set the address to use for the Control Connection
        in such cases where Lightstreamer is behind a Load Balancer.
        """
        if custom_address is None:
            self._control_url = self._base_url
        else:
            self._control_url = f"{self._base_url.split('/')[0]}//{custom_address}"

    def _control(self, params):
        """Create a Control Connection to send control commands
        that manage the content of Stream Connection.
        """
        params["LS_session"] = self._session["SessionId"]
        response = self._call(self._control_url, CONTROL_URL_PATH, params)
        decoded_response = response.readline().decode("utf-8").rstrip()
        log.debug("Server response: <%s>", decoded_response)
        return decoded_response

    def _read_from_stream(self):
        """Read a single line of content of the Stream Connection."""
        return self._stream_connection.readline().decode("utf-8").rstrip()

    def set_password(self, password):
        log.debug("Set password to <%s>", f'{password[:3]}{"*"*(len(password)-6)}{password[-3:]}')
        self._password = password

    def set_username(self, username):
        log.debug("Set username to <%s>", username)
        self._username = username

    def connect(self):
        """Establish a connection to Lightstreamer Server to create a new
        session.
        """
        log.debug("Opening a new session to <%s>", self._base_url)
        self._stream_connection = self._call(
            self._base_url,
            CONNECTION_URL_PATH,
            {
                "LS_op2": 'create',
                "LS_cid": 'mgQkwtwdysogQz2BJ4Ji kOj2Bg',
                "LS_adapter_set": self._adapter_set,
                "LS_user": self._username,
                "LS_password": self._password,
            },
        )
        stream_line = self._read_from_stream()
        log.debug("Stream line is <%s>", stream_line)
        self._handle_stream(stream_line)

    @property
    def is_connect(self):
        return bool(self._session.get('SessionId'))

    def bind(self):
        """Replace a completely consumed connection in listening for an active
        Session.
        """
        log.debug("Binding to <%s>", self._control_url.geturl())
        self._stream_connection = self._call(
            self._control_url, BIND_URL_PATH, {"LS_session": self._session["SessionId"]}
        )

        self._bind_counter += 1
        stream_line = self._read_from_stream()
        self._handle_stream(stream_line)
        log.info("Bound to <%s>", self._control_url.geturl())

    def _handle_stream(self, stream_line):
        if stream_line == OK_CMD:
            log.info("Successfully connected to <%s>", self._base_url)
            log.debug("Starting to handling real-time stream")
            # Parsing session inkion
            while 1 and (next_stream_line := self._read_from_stream()):
                session_key, session_value = next_stream_line.split(":", 1)
                self._session[session_key] = session_value
            # Setup of the control link url
            self._set_control_link_url(self._session.get("ControlAddress"))

            # Start a new thread to handle real time updates sent
            # by Lightstreamer Server on the stream connection.
            self._stream_connection_thread = threading.Thread(
                name="StreamThread-{0}".format(self._bind_counter), target=self._receive
            )
            self._stream_connection_thread.setDaemon(True)
            self._stream_connection_thread.start()
            log.info("Started handling of real-time stream")
        else:
            lines = self._stream_connection.readlines()
            lines.insert(0, stream_line)

            log.error("\nServer response error: \n%s", "".join([str(line) for line in lines]))
            raise IOError()

    def _join(self):
        """Await the natural StreamThread termination."""
        if self._stream_connection_thread:
            log.debug("Waiting for thread to terminate")
            self._stream_connection_thread.join()
            self._stream_connection_thread = None
            log.debug("Thread terminated")

    def disconnect(self):
        """Request to close the session previously opened with the connect()
        invocation.
        """
        if self._stream_connection is not None:
            log.debug("Closing session to <%s>", self._base_url)
            _ = self._control({"LS_op": OP_DESTROY})
            # There is no need to explicitly close the connection, since it is
            # handled by thread completion.
            self._join()
            log.info("Closed session to <%s>", self._base_url)
        else:
            log.warning("No connection to Lightstreamer")

    def subscribe(self, subscription):
        """ "Perform a subscription request to Lightstreamer Server."""
        # Register the Subscription with a new subscription key
        self._current_subscription_key += 1
        self._subscriptions[self._current_subscription_key] = subscription

        # Send the control request to perform the subscription
        log.debug("Making a new subscription request")
        server_response = self._control(
            {
                "LS_table": self._current_subscription_key,
                "LS_op": OP_ADD,
                "LS_data_adapter": subscription.adapter,
                "LS_mode": subscription.mode,
                "LS_schema": " ".join(subscription.field_names),
                "LS_id": " ".join(subscription.item_names),
            }
        )
        if server_response == OK_CMD:
            log.info("Successfully subscribed ")
        else:
            log.warning("Subscription error")
        return self._current_subscription_key

    def unsubscribe(self, subcription_key):
        """Unregister the Subscription associated with the
        specified subscription_key.
        """
        log.debug("Making an unsubscription request")
        if subcription_key in self._subscriptions:
            server_response = self._control({"LS_Table": subcription_key, "LS_op": OP_DELETE})

            if server_response == OK_CMD:
                del self._subscriptions[subcription_key]
                log.info("Successfully unsubscribed")
            else:
                log.warning("Unsubscription error")
        else:
            log.warning("No subscription key %s found!", subcription_key)

    def _forward_update_message(self, update_message):
        """Forwards the real time update to the relative
        Subscription instance for further dispatching to its listeners.
        """
        log.debug("Received update message: <%s>", update_message)
        try:
            tok = update_message.split(',', 1)
            table, item = int(tok[0]), tok[1]
            if table in self._subscriptions:
                self._subscriptions[table].notifyupdate(item)
            else:
                log.warning("No subscription found!")
        except Exception:
            print(traceback.format_exc())

    def _receive(self):
        rebind = False
        receive = True
        while receive:
            log.debug("Waiting for a new message")
            try:
                message = self._read_from_stream()
                log.debug("Received message: <%s>", message)
                if not message.strip():
                    message = None
            except Exception:
                log.error("Communication error")
                print(traceback.format_exc())
                message = None

            if message is None:
                receive = False
                log.warning("No new message received")
            elif message == PROBE_CMD:
                # Skipping the PROBE message, keep on receiving messages.
                log.debug("PROBE message")
            elif message.startswith(ERROR_CMD):
                # Terminate the receiving loop on ERROR message
                receive = False
                log.error("ERROR")
            elif message.startswith(LOOP_CMD):
                # Terminate the the receiving loop on LOOP message.
                # A complete implementation should proceed with
                # a rebind of the session.
                log.debug("LOOP")
                receive = False
                rebind = True
            elif message.startswith(SYNC_ERROR_CMD):
                # Terminate the receiving loop on SYNC ERROR message.
                # A complete implementation should create a new session
                # and re-subscribe to all the old items and relative fields.
                log.error("SYNC ERROR")
                receive = False
            elif message.startswith(END_CMD):
                # Terminate the receiving loop on END message.
                # The session has been forcibly closed on the server side.
                # A complete implementation should handle the
                # "cause_code" if present.
                log.info("Connection closed by the server")
                receive = False
            elif message.startswith("Preamble"):
                # Skipping Preamble message, keep on receiving messages.
                log.debug("Preamble")
            else:
                self._forward_update_message(message)

        if not rebind:
            log.debug("No rebind to <%s>, clearing internal session data", self._base_url)
            # Clear internal data structures for session
            # and subscriptions management.
            self._stream_connection = None
            self._session.clear()
            self._subscriptions.clear()
            self._current_subscription_key = 0
        else:
            log.debug("Binding to this active session")
            self.bind()
