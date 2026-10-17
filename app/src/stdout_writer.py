import sys

class StdoutWriter:
    """Write messages to standard output and flush them immediately."""

    @staticmethod
    def write(message: str):
        """Write ``message`` to stdout and flush the output stream."""
        sys.stdout.write(message)
        sys.stdout.flush()