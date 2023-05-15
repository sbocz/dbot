import json
import os


class DataAccessor:
    brain_path: str

    def __init__(self, brain_path: str):
        self.brain_path = brain_path

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.brain_path, filename)

    def set_brain_path(self, brain_path: str) -> None:
        self.brain_path = brain_path

    def read_json_from_file(self, filename: str):
        """Reads the content from a JSON file"""
        with open(self._get_file_path(filename), "r") as json_file:
            result = json.load(json_file)
        return result

    def write_json_to_file(self, filename: str, data) -> None:
        """Writes the provided data to a JSON file"""
        with open(self._get_file_path(filename), "w") as json_file:
            json.dump(data, json_file)
        return


default_accessor = DataAccessor(brain_path="../data")


def set_brain_path(path: str):
    default_accessor.set_brain_path(path)


def read_json_from_file(filename):
    return default_accessor.read_json_from_file(filename=filename)


def write_json_to_file(filename, data) -> None:
    default_accessor.write_json_to_file(filename=filename, data=data)
    return
