import pathlib

import pytest
from fs.memoryfs import MemoryFS

from dependency_graph.models import VirtualPath


def test_virtualpath_creation():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "some", "path")
    assert isinstance(vpath, VirtualPath)
    assert vpath.relative_fs_path == "some/path"


def test_virtualpath_is_dir():
    mem_fs = MemoryFS()
    mem_fs.makedir("somedir")
    vpath = VirtualPath(mem_fs, "somedir")
    assert vpath.is_dir()


def test_virtualpath_is_file():
    mem_fs = MemoryFS()
    mem_fs.touch("somefile")
    vpath = VirtualPath(mem_fs, "somefile")
    assert vpath.is_file()


def test_virtualpath_mkdir():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "newdir")
    vpath.mkdir()
    assert vpath.exists()
    assert vpath.is_dir()


def test_virtualpath_touch():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "newfile")
    vpath.touch()
    assert vpath.exists()
    assert vpath.is_file()


def test_virtualpath_open_read_write():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "newfile")
    vpath.touch()
    with vpath.open("w") as f:
        f.write("Hello World")
    with vpath.open() as f:
        content = f.read()
    assert content == "Hello World"


def test_virtualpath_rename():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "oldname")
    vpath.touch()
    new_vpath = VirtualPath(mem_fs, "newname")
    vpath.rename(new_vpath)
    assert new_vpath.exists()
    assert not vpath.exists()


def test_virtualpath_rmdir():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir")
    vpath.mkdir()
    vpath.rmdir()
    assert not vpath.exists()


def test_virtualpath_unlink():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    vpath.unlink()
    assert not vpath.exists()


def test_virtualpath_exists():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    assert not vpath.exists()
    vpath.touch()
    assert vpath.exists()


def test_virtualpath_relative_to():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir", "subdir", "file")
    base_vpath = VirtualPath(mem_fs, "dir")
    relative_path = vpath.relative_to(base_vpath)
    assert relative_path == VirtualPath(mem_fs, "subdir/file")


def test_virtualpath_relative_to_a_string():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir", "subdir", "file")
    base_vpath_str = "dir"
    relative_path = vpath.relative_to(base_vpath_str)
    assert relative_path == VirtualPath(mem_fs, "subdir/file")


def test_virtualpath_chmod():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    with pytest.raises(NotImplementedError):
        vpath.chmod(0o644)


def test_virtualpath_symlink_to():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    with pytest.raises(NotImplementedError):
        vpath.symlink_to("other")


def test_virtualpath_is_block_device():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert not vpath.is_block_device()


def test_virtualpath_is_char_device():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert not vpath.is_char_device()


def test_virtualpath_is_fifo():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert not vpath.is_fifo()


def test_virtualpath_is_socket():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert not vpath.is_socket()


def test_virtualpath_is_symlink():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert not vpath.is_symlink()


def test_virtualpath_iterdir():
    mem_fs = MemoryFS()
    mem_fs.makedir("dir")
    mem_fs.touch("dir/file1")
    mem_fs.touch("dir/file2")
    vpath = VirtualPath(mem_fs, "dir")
    items = list(vpath.iterdir())
    assert len(items) == 2
    assert VirtualPath(mem_fs, "dir/file1") in items
    assert VirtualPath(mem_fs, "dir/file1") in items


def test_virtualpath_glob():
    mem_fs = MemoryFS()
    mem_fs.makedir("dir")
    mem_fs.touch("dir/file1")
    mem_fs.touch("dir/file2")
    vpath = VirtualPath(mem_fs, "dir")
    matches = list(vpath.glob("file*"))
    assert len(matches) == 2
    assert VirtualPath(mem_fs, "/dir/file1") in matches
    assert VirtualPath(mem_fs, "/dir/file2") in matches

def test_virtualpath_glob_1():
    mem_fs = MemoryFS()
    mem_fs.makedir("/dir")
    mem_fs.touch("/dir/file1")
    mem_fs.touch("/dir/file2")
    vpath = VirtualPath(mem_fs, "/dir")
    matches = list(vpath.glob("file*"))
    assert len(matches) == 2
    assert VirtualPath(mem_fs, "/dir/file1") in matches
    assert VirtualPath(mem_fs, "/dir/file2") in matches


def test_virtualpath_rglob():
    mem_fs = MemoryFS()
    mem_fs.makedirs("/dir/subdir")
    mem_fs.touch("/dir/subdir/file1")
    mem_fs.touch("/dir/file2")
    vpath = VirtualPath(mem_fs, "dir")
    matches = list(vpath.rglob("file*"))
    assert len(matches) == 2
    assert VirtualPath(mem_fs, "/dir/file2") in matches
    assert VirtualPath(mem_fs, "/dir/subdir/file1") in matches


def test_virtualpath_owner():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert vpath.owner() is None  # MemoryFS does not implement owners


def test_virtualpath_group():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    assert vpath.group() is None  # MemoryFS does not implement groups


def test_virtualpath_stat():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    vpath_stat = vpath.stat()
    assert vpath_stat is None


def test_virtualpath_lstat():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file")
    vpath.touch()
    vpath_lstat = vpath.lstat()
    assert vpath_lstat is None


def test_virtualpath_representations():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "somefile")
    assert vpath.relative_fs_path == "somefile"
    assert vpath.as_pathlib_path() == pathlib.Path("somefile")
    assert vpath.as_posix() == "somefile"
    assert vpath.as_str() == "somefile"
    assert str(vpath) == "somefile"
    assert repr(vpath) == f"VirtualPath({mem_fs}, 'somefile')"
    assert isinstance(vpath.__hash__(), int)


def test_virtualpath_joinpath():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir")
    new_vpath = vpath.joinpath("subdir/file")
    assert new_vpath == VirtualPath(mem_fs, "dir", "subdir", "file")


def test_virtualpath_truediv():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir")
    new_vpath = vpath / "subdir"
    assert new_vpath == VirtualPath(mem_fs, "dir", "subdir")


def test_virtualpath_with_name():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/file.txt")
    new_vpath = vpath.with_name("newfile.txt")
    assert new_vpath == VirtualPath(mem_fs, "dir", "newfile.txt")


def test_virtualpath_with_suffix():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "file.txt")
    new_vpath = vpath.with_suffix(".md")
    assert new_vpath == VirtualPath(mem_fs, "file.md")


def test_virtualpath_parent():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir/file")
    parent_vpath = vpath.parent
    assert parent_vpath == VirtualPath(mem_fs, "dir/subdir")


def test_virtualpath_parents():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir/file")
    parents = vpath.parents
    assert parents == [
        VirtualPath(mem_fs, "dir/subdir"),
        VirtualPath(mem_fs, "dir"),
        VirtualPath(mem_fs, "."),
    ]


def test_virtualpath_with_segments():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir")
    new_path = vpath.with_segments("new", "path")
    assert isinstance(new_path, VirtualPath)
    assert new_path.relative_fs_path == "new/path"


def test_virtualpath_is_relative_to():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir/file")
    base_vpath = VirtualPath(mem_fs, "dir")
    assert vpath.is_relative_to(base_vpath)
    unrelated_vpath = VirtualPath(mem_fs, "otherdir")
    assert not vpath.is_relative_to(unrelated_vpath)


def test_virtualpath_is_relative_to_a_string():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir/file")
    base_vpath_str = "dir"
    assert vpath.is_relative_to(base_vpath_str)
    unrelated_vpath_str = "otherdir"
    assert not vpath.is_relative_to(unrelated_vpath_str)


def test_virtualpath_absolute():
    mem_fs = MemoryFS()
    vpath = VirtualPath(mem_fs, "dir/subdir/file")
    assert vpath.absolute() == VirtualPath(mem_fs, '/dir/subdir/file')
