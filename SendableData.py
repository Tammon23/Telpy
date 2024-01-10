from constants import MAX_BYTE_TRANSFER
from dataclasses import dataclass
from uuid import UUID
import pickle


class SendableData:
    def get_as_bytes(self, max_fragment_size: int = MAX_BYTE_TRANSFER) -> list[bytes]:
        dump = pickle.dumps(self)
        res = [dump[i:i + max_fragment_size] for i in range(0, len(dump), max_fragment_size)]
        return [len(res).to_bytes(4, byteorder='big')] + res


@dataclass
class Profile(SendableData):
    name: str = None
    uuid: UUID = None

    def __repr__(self):
        return f'<Profile: name={self.name} uuid={self.uuid}>'


@dataclass
class Text(SendableData):
    data: str
    source: Profile = None

    def __repr__(self):
        return f"<Text: data={self.data} source={repr(self.source)}>"


@dataclass
class ServerCommand(SendableData):
    name: str
    args: list[str]
    pattern: str = "/"

    def __repr__(self):
        return f"<ServerCommand: pattern={self.pattern} name={self.name} args={self.args} source={repr(self.source)}>"
