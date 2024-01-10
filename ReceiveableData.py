from SendableData import SendableData
import pickle


class ReceiveableData:
    def get_from_bytes(self, data: list[bytes]) -> SendableData:
        return pickle.loads(b"".join(data))