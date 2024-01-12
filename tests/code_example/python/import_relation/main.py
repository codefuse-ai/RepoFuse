import os
from pathlib import Path
from x import *
import y

print(os.cpu_count())
Path(__file__)

func_x()

X()

y.VAR_Y += 1


def test_import():
    from z import func_z

    func_z()
