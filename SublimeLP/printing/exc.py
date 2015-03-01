from contextlib import contextmanager
from functools import wraps
import subprocess


class PrintSystemError(Exception):
    pass


@contextmanager
def error_wrap():
    try:
        yield
    except OSError as e:
        raise PrintSystemError('OSError: {}'.format(e))
    except subprocess.CalledProcessError as e:
        raise PrintSystemError('{} failed ({}): {}'.format(
            e.cmd, e.returncode, e.output
        ))


def wrap_errors(f):
    @wraps(f)
    def _(*args, **kwargs):
        with error_wrap():
            return f(*args, **kwargs)

    return _
