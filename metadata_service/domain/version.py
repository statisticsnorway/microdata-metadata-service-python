from dataclasses import dataclass


@dataclass
class Version:
    major: str
    minor: str
    patch: str
    draft: str

    def __init__(self, version: str):
        split = version.split('.')
        self.major = split[0]
        self.minor = split[1]
        self.patch = split[2]
        self.draft = split[3]

    def to_3_underscored(self):
        return '_'.join([self.major, self.minor, self.patch])

    def to_4_dotted(self):
        return '.'.join([self.major, self.minor, self.patch, self.draft])

    def is_draft(self):
        return self.major == '0' \
               and self.minor == '0'\
               and self.patch == '0'

    def __str__(self):
        return ".".join([self.major, self.minor, self.patch, self.draft])
