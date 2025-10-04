import tarfile
from glob import iglob
from io import BytesIO
from os import path, getcwd, chdir
from urllib.request import urlopen
from zipfile import ZipFile
from pathlib import Path
from struct import pack, unpack

import pytest
from pytest import TempPathFactory

from fastlz import compress, decompress


@pytest.fixture(scope='session')
def get_corpus_dir(tmp_path_factory: TempPathFactory) -> Path:
    download_dir = tmp_path_factory.mktemp("download-unpack")
    corpus_dir = tmp_path_factory.mktemp("corpus")

    response = urlopen("https://github.com/MiloszKrajewski/SilesiaCorpus/archive/refs/heads/master.zip")
    with ZipFile(BytesIO(response.read())) as archive:
        archive.extractall(download_dir)
        oldpwd = getcwd()
        chdir(download_dir)
        try:
            for i in iglob("*/*.zip", recursive=True):
                with ZipFile(i) as archive:
                    archive.extractall(path.join(corpus_dir, "silesia"))
        finally:
            chdir(oldpwd)

    response = urlopen("http://corpus.canterbury.ac.nz/resources/cantrbry.tar.gz")
    with tarfile.open(fileobj=BytesIO(response.read())) as archive:
        archive.extractall(path.join(corpus_dir, "canterbury"))

    return corpus_dir


@pytest.mark.parametrize("filename", [
    "silesia/x-ray",
    "silesia/dickens",
    "silesia/ooffice",
    "silesia/sao",
    "silesia/reymont",
    "silesia/mr",
    "silesia/mozilla",
    "silesia/webster",
    "silesia/samba",
    "silesia/osdb",
    "silesia/nci",
    "silesia/xml",
    "canterbury/ptt5",
    "canterbury/xargs.1",
    "canterbury/asyoulik.txt",
    "canterbury/kennedy.xls",
    "canterbury/plrabn12.txt",
    "canterbury/grammar.lsp",
    "canterbury/cp.html",
    "canterbury/lcet10.txt",
    "canterbury/alice29.txt",
    "canterbury/sum",
    "canterbury/fields.c",
])
def test_compress_uncompress_compare(get_corpus_dir: Path, filename: str):
    """try with some corpuses used in fastlz"""
    corpus_dir = get_corpus_dir
    with open(path.join(corpus_dir, filename), "rb") as f:
        uncompressed = f.read()
        compressed, length = compress(uncompressed)
        uncompressed_2 = decompress(compressed, length)
        print(f"filename: {filename} | sizes: {len(uncompressed)} -> {len(compressed)}")
        assert uncompressed == uncompressed_2


@pytest.mark.parametrize("content", [
    b"",
    b"\x00",
    b"\xFF",
    b"\x01",
    b"\x00\x00",
    b"\xFF\xFF",
    b"\x01\x01",
    b"\x00\x00\x00",
    b"\xFF\xFF\xFF",
    b"\x01\x01\x01",
    b"\x00\x00\x00\x00",
    b"\xFF\xFF\xFF\xFF",
    b"\x01\x01\x01\x01",
    b"\x01hello\x00world\x00\x00",
])
def test_compress_compress(content: bytes):
    cnt = 100
    d = content
    lengths = []
    # compression of compressions
    for i in range(cnt):
        d, orig_len = compress(d)
        lengths.append(orig_len)
    # decompress compression of compressions
    for i in range(cnt):
        d = decompress(d, lengths.pop())
    assert d == content


@pytest.mark.parametrize("content", [
    (b"", "00000000"),
    (b"\x00", "010000000000"),
    (b"\xFF", "0100000000ff"),
    (b"\x01", "010000000001"),
    (b"\x00\x00", "02000000010000"),
    (b"\xFF\xFF", "0200000001ffff"),
    (b"\x01\x01", "02000000010101"),
    (b"\x01hello\x00world\x00\x00", "0e0000000d0168656c6c6f00776f726c640000"),
])
def test_version_001(content: bytes):
    """compare with previous version"""
    (u_ref, c_ref) = content[0], bytes.fromhex(content[1])

    # Test new compress against old format
    compressed, orig_len = compress(u_ref)
    c = pack('<I', orig_len) + compressed
    assert c == c_ref

    # Test new decompress with old format
    original_size = unpack('<I', c_ref[:4])[0]
    u = decompress(c_ref[4:], original_size)
    assert u_ref == u