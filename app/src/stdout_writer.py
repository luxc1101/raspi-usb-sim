import sys

class StdoutWriter:
    @staticmethod
    def write(message: str):
        sys.stdout.write(message)
        sys.stdout.flush()