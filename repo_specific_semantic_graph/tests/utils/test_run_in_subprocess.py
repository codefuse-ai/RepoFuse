import ctypes
from time import sleep

import pytest

from dependency_graph.utils.run_in_subprocess import SubprocessRunner


# This is an example C code snippet that is assumed to cause a segmentation fault.
def c_function():
    # Create a pointer and access an invalid memory address.
    ptr = ctypes.c_int.from_address(0x12345678)
    # Return the value pointed to by the pointer.
    return ptr.value


def raise_error():
    raise NotImplementedError("test")


def test_run_within_timeout():
    with pytest.raises(TimeoutError, match="Process timed out after 1 seconds"):
        SubprocessRunner(
            lambda: sleep(5),
        ).run(timeout=1)


def test_run_will_crash():
    with pytest.raises(RuntimeError, match="Process crashed with exit code:"):
        SubprocessRunner(
            c_function,
        ).run(timeout=1)


def test_run_will_reraise_error():
    with pytest.raises(NotImplementedError, match="test"):
        SubprocessRunner(
            raise_error,
        ).run(timeout=1)


def test_run_can_accept_args():
    result = SubprocessRunner(lambda x: x + 1, 1).run(timeout=1)
    assert result == 2
