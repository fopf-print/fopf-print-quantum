from dataclasses import dataclass


@dataclass
class BusinessLogicFucked(Exception):
    msg: list[str]
