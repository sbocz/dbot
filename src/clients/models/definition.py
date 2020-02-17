import logging
import re

log = logging.getLogger('discord')


class Definition:

    def __init__(self, definition: str, permalink: str, author: str, word: str, example: str):
        self.example = re.sub(r"[\[\]]", "", example)
        self.word = re.sub(r"[\[\]]", "", word)
        self.author = author
        self.permalink = permalink
        self.definition = re.sub(r"[\[\]]", "", definition)

    @staticmethod
    def from_dict(d):
        return Definition(
            str(d['definition']), str(d['permalink']), str(d['author']), str(d['word']), str(d['example']))
