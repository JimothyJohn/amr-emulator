from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="RobotIdentity")


@_attrs_define
class RobotIdentity:
    """
    Attributes:
        robot_id (str):
        serial_number (str):
        name (str):
        model (str):
        software_version (str):
        ip (str):
        timestamp (datetime.datetime | None | Unset):
    """

    robot_id: str
    serial_number: str
    name: str
    model: str
    software_version: str
    ip: str
    timestamp: datetime.datetime | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_id = self.robot_id

        serial_number = self.serial_number

        name = self.name

        model = self.model

        software_version = self.software_version

        ip = self.ip

        timestamp: None | str | Unset
        if isinstance(self.timestamp, Unset):
            timestamp = UNSET
        elif isinstance(self.timestamp, datetime.datetime):
            timestamp = self.timestamp.isoformat()
        else:
            timestamp = self.timestamp

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "robot-id": robot_id,
                "serial-number": serial_number,
                "name": name,
                "model": model,
                "software-version": software_version,
                "ip": ip,
            }
        )
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        robot_id = d.pop("robot-id")

        serial_number = d.pop("serial-number")

        name = d.pop("name")

        model = d.pop("model")

        software_version = d.pop("software-version")

        ip = d.pop("ip")

        def _parse_timestamp(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                timestamp_type_0 = datetime.datetime.fromisoformat(data)

                return timestamp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        timestamp = _parse_timestamp(d.pop("timestamp", UNSET))

        robot_identity = cls(
            robot_id=robot_id,
            serial_number=serial_number,
            name=name,
            model=model,
            software_version=software_version,
            ip=ip,
            timestamp=timestamp,
        )

        return robot_identity
