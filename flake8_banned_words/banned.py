# Copyright (C) 2019 Pablo Alvarez de Sotomayor Posadillo

# This file is part of flake8_banned_words.

# flake8_banned_words is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# flake8_banned_words is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#Public License for more details.

# You should have received a copy of the GNU General Public License along with
# flake8_banned_words. If not, see <http://www.gnu.org/licenses/>.

import ast
import pycodestyle
import re

from collections import namedtuple

from flake8_banned_words import __version__
from flake8_banned_words.visitor import Visitor

Error = namedtuple('Error', ['lineno', 'code', 'message'])


class BannedWords(object):
    name = "banned-words"
    version = __version__

    def __init__(self, tree, filename, lines=None):
        self.filename = filename
        self.tree = tree
        self.lines = lines
        self.words = []
        self.errors = []

    def error(self, error):
        return (
            error.lineno,
            0,
            "{0} {1}".format(error.code, error.message),
            GlobalVariables,
        )

    @classmethod
    def add_options(cls, parser):
        register_opt(
            parser,
            "--banned-words",
            default="",
            action="store",
            type="string",
            help="Banned words in the comments",
            parse_from_config=True,
            comma_separated_list=True,
        )

    @classmethod
    def parse_options(cls, options):
        optdict = {}

        words = options.banned_words
        if not isinstance(banned_words, list):
            words = options.banned_words.split(",")

        optdict = dict(
            banned_words=[w.strip() for w in words],
        )

        cls.options = optdict

    def run(self):
        for error in self.check():
            yield error

    def load_file(self):
        if self.filename in ("stdin", "-", None):
            self.filename = "stdin"
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

        if self.tree is None:
            self.tree = ast.parse(''.join(self.lines))

    def check(self):
        if not self.tree or not self.lines:
            self.load_file()

        self.check_inline_comments()
        for err in self.errors:
            yield self.error(err)

    def check_inline_comments(self):
        comment_pattern = re.compile(r'^(?:[^"/\\]|\"(?:[^\"\\]|\\.)*\"|/(?:[^/"\\]|\\.)|/\"(?:[^\"\\]|\\.)*\"|\\.)*#(.*)$')

        lineno = 0
        for line in self.lines:
            lineno += 1
            comment = comment_pattern.match(line)
            if comment == None:
                continue

            for word in self.words:
                if comment.find(word):
                    self.errors.append(Error(lineno, 'E001',
                                             'Word {0} find inside a comment'.format(word)))
def register_opt(parser, *args, **kwargs):
    parser.add_option(*args, **kwargs)
