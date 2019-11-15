import re


# Most common regex chunks for *.cfg files.
OPENING_BRACKET = r'\s*\(\s*'
CLOSING_BRACKET = r'\s*\)\s*'
COMMA = r'\s*,\s*'
QUOTED_STRING = r'"((?:[^"\\]|\\.)*)"'
INT_VALUE = r'(\d+)'
COMMENT = r'#?.*'


def create_regex(*args):
    return re.compile(''.join(args))
