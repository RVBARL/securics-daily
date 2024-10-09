# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import json
import socket
from typing import Any

from securics.core.common import origin_module
from securics.core.exception import SecuricsError, SecuricsInternalError
from securics.core.securics_socket import create_securics_socket_message


def create_securics_queue_socket_msg(flag: str, str_agent_id: str, msg: str, is_restart: bool = False) -> str:
    """Create message that will be sent to the SecuricsQueue socket.

    Parameters
    ----------
    flag : str
        Flag used to determine if the message will be sent to a specific agent or to all agents.
    str_agent_id : str
        String indicating the agent_id if the message will be sent to a specific agent, or '(null)' if it will be sent
        to all agents.
    msg : str
        Message to be sent to the agent or agents.
    is_restart : bool
        Indicates whether the message sent is a restart message or not. Default `False`

    Returns
    -------
    str
        Message that will be sent to the SecuricsQueue socket.
    """
    return f"(msg_to_agent) [] {flag} {str_agent_id} {msg}" if not is_restart else \
        f"(msg_to_agent) [] {flag} {str_agent_id} {msg} - null (from_the_server) (no_rule_id)"


class BaseQueue:
    # Sizes
    OS_MAXSTR = 6144  # OS_SIZE_6144
    MAX_MSG_SIZE = OS_MAXSTR + 256

    def __init__(self, path):
        self.path = path
        self._connect()

    def _connect(self):
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.socket.connect(self.path)
            length_send_buffer = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            if length_send_buffer < SecuricsQueue.MAX_MSG_SIZE:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SecuricsQueue.MAX_MSG_SIZE)
        except Exception:
            raise SecuricsInternalError(1010, self.path)

    def __enter__(self):
        return self

    def _send(self, msg: bytes) -> None:
        """Send a message through a socket.

        Parameters
        ----------
        msg : bytes
            The message to send.

        Raises
        ------
        SecuricsInternalError(1011)
            If there was an error communicating with queue.
        """
        try:
            sent = self.socket.send(msg)

            if sent == 0:
                raise SecuricsInternalError(1011, self.path)
        except socket.error:
            raise SecuricsInternalError(1011, self.path)

    def close(self):
        self.socket.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SecuricsQueue(BaseQueue):
    """
    SecuricsQueue Object.
    """

    # Messages
    HC_SK_RESTART = "syscheck restart"  # syscheck restart
    HC_FORCE_RECONNECT = "force_reconnect"  # force reconnect command
    RESTART_AGENTS = "restart-ossec0"  # Agents, not manager (000)
    RESTART_AGENTS_JSON = json.dumps(create_securics_socket_message(origin={'module': origin_module.get()},
                                                                 command="restart-securics0",
                                                                 parameters={"extra_args": [],
                                                                             "alert": {}}))  # Agents, not manager (000)

    # Types
    AR_TYPE = "ar-message"

    def send_msg_to_agent(self, msg: str = '', agent_id: str = '', msg_type: str = '') -> str:
        """Send message to agent.

        Active-response
          Agents: /var/ossec/queue/alerts/ar
            - Existing command:
              - (msg_to_agent) [] NNS 001 restart-ossec0 arg1 arg2 arg3
              - (msg_to_agent) [] ANN (null) restart-ossec0 arg1 arg2 arg3
            - Custom command:
              - (msg_to_agent) [] NNS 001 !test.sh arg1 arg2 arg3
              - (msg_to_agent) [] ANN (null) !test.sh arg1 arg2 arg3
          Agents with version >= 4.2.0:
            - Existing and custom commands:
              - (msg_to_agent) [] NNS 001 {JSON message}
          Manager: /var/ossec/queue/alerts/execq
            - Existing or custom command:
              - {JSON message}

        Parameters
        ----------
        msg : str
            Message to be sent to the agent.
        agent_id : str
            ID of the agent we want to send the message to.
        msg_type : str
            Message type.

        Raises
        ------
        SecuricsInternalError(1012)
            If the message was invalid to queue.
        SecuricsError(1014)
            If there was an error communicating with socket.

        Returns
        -------
        str
            Message confirming the message has been sent.
        """
        # Variables to check if msg is a non active-response message or a restart message
        msg_is_no_ar = msg in [SecuricsQueue.HC_SK_RESTART, SecuricsQueue.HC_FORCE_RECONNECT]
        msg_is_restart = msg in [SecuricsQueue.RESTART_AGENTS, SecuricsQueue.RESTART_AGENTS_JSON]

        # Create flag and string used to specify the agent ID
        if agent_id:
            flag = 'NNS' if not msg_is_no_ar else 'N!S'
            str_agent_id = agent_id
        else:
            flag = 'ANN' if not msg_is_no_ar else 'A!N'
            str_agent_id = '(null)'

        # AR
        if msg_type == SecuricsQueue.AR_TYPE:
            socket_msg = create_securics_queue_socket_msg(flag, str_agent_id, msg) if agent_id != '000' else msg
            # Return message
            ret_msg = "Command sent."

        # NO-AR: Restart syscheck and reconnect
        # Restart agents
        else:
            # If msg is not a non active-response command and not a restart command, raises SecuricsInternalError
            if not msg_is_no_ar and not msg_is_restart:
                raise SecuricsInternalError(1012, msg)
            socket_msg = create_securics_queue_socket_msg(flag, str_agent_id, msg, is_restart=msg_is_restart)
            # Return message
            if msg == SecuricsQueue.HC_SK_RESTART:
                ret_msg = "Restarting Syscheck on agent" if agent_id else "Restarting Syscheck on all agents"
            elif msg == SecuricsQueue.HC_FORCE_RECONNECT:
                ret_msg = "Reconnecting agent" if agent_id else "Reconnecting all agents"
            else:  # msg == SecuricsQueue.RESTART_AGENTS or msg == SecuricsQueue.RESTART_AGENTS_JSON
                ret_msg = "Restarting agent" if agent_id else "Restarting all agents"

        try:
            # Send message
            self._send(socket_msg.encode())
        except:
            raise SecuricsError(1014, extra_message=f": SecuricsQueue socket with path {self.path}")

        return ret_msg


class SecuricsAnalysisdQueue(BaseQueue):
    """
    SecuricsAnalysisdQueue Object.
    """

    MAX_MSG_SIZE = 65535

    def _connect(self):
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.socket.connect(self.path)
        except Exception:
            raise SecuricsInternalError(1010, self.path)

    def send_msg(self, msg_header: str, msg: str):
        """Send message to analysisd.

        Parameters
        ----------
        msg_header : str
            Header message to attach.
        msg : str
            Message to send.

        Raises
        ------
        SecuricsInternalError(1012)
            If the size of the event is bigger than the message size that analysisd can handle.
        SecuricsError(1014)
            If there was an error communicating with socket.
        """
        socket_msg = f"{msg_header}{msg}".encode()

        if len(socket_msg) > self.MAX_MSG_SIZE:
            raise SecuricsError(
                1012,
                f"The event is too large to be sent to analysisd (maximum is {self.MAX_MSG_SIZE}B)"
            )

        try:
            # Send message
            self._send(socket_msg)
        except Exception as e:
            raise SecuricsError(1014, extra_message=f': SecuricsAnalysisdQueue socket with path {self.path}. {str(e)}')
