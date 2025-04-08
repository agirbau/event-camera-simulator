
import sys
import os
import logging
import tempfile
from contextlib import contextmanager

@contextmanager
def capture_blender_output():
    logger = logging.getLogger()
    """Redirect Blender C-level stdout/stderr to Python logger."""
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()

    stdout_temp = tempfile.TemporaryFile(mode='w+b')
    stderr_temp = tempfile.TemporaryFile(mode='w+b')

    saved_stdout = os.dup(original_stdout_fd)
    saved_stderr = os.dup(original_stderr_fd)

    os.dup2(stdout_temp.fileno(), original_stdout_fd)
    os.dup2(stderr_temp.fileno(), original_stderr_fd)

    try:
        yield
    finally:
        sys.stdout.flush()
        sys.stderr.flush()

        os.dup2(saved_stdout, original_stdout_fd)
        os.dup2(saved_stderr, original_stderr_fd)

        os.close(saved_stdout)
        os.close(saved_stderr)

        stdout_temp.seek(0)
        stderr_temp.seek(0)

        stdout_output = stdout_temp.read().decode()
        stderr_output = stderr_temp.read().decode()

        if stdout_output.strip():
            for logitems in stdout_output.strip().splitlines():
                logger.debug(logitems)
        if stderr_output.strip():
            for logitems in stdout_output.strip().splitlines():
                logger.error(logitems)

        stdout_temp.close()
        stderr_temp.close()
