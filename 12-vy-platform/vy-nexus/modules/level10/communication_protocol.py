# communication_protocol.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import time
import uuid


@dataclass(frozen=True)
class Message:
    msg_id: str
    topic: str
    sender: str
    ts: float
    payload: Dict[str, Any]


class CommunicationProtocol:
    """
    Simple in-memory message constructor. (No network yet.)
    Stable contract for future distributed upgrade.
    """

    def new_message(self, topic: str, sender: str, payload: Optional[Dict[str, Any]] = None) -> Message:
        return Message(
            msg_id=str(uuid.uuid4()),
            topic=topic,
            sender=sender,
            ts=time.time(),
            payload=payload or {},
        )

    def serialize(self, msg: Message) -> Dict[str, Any]:
        return {
            "msg_id": msg.msg_id,
            "topic": msg.topic,
            "sender": msg.sender,
            "ts": msg.ts,
            "payload": msg.payload,
        }
