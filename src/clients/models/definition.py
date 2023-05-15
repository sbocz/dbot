import logging
import re

log = logging.getLogger("discord")


class Definition:
    """A definition data object"""

    def __init__(
        self, definition: str, permalink: str, author: str, word: str, example: str
    ):
        self.example = re.sub(r"[\[\]]", "", example)
        self.word = re.sub(r"[\[\]]", "", word)
        self.author = author
        self.permalink = permalink
        self.definition = re.sub(r"[\[\]]", "", definition)

    @staticmethod
    def from_dict(dictionary):
        """Convert a dictionary to a definition"""
        return Definition(
            str(dictionary["definition"]),
            str(dictionary["permalink"]),
            str(dictionary["author"]),
            str(dictionary["word"]),
            str(dictionary["example"]),
        )
