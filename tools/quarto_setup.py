"""Install the pinned Quarto into the repository, and find it for later callers.

Run from the repository root:

    .venv/bin/python tools/quarto_setup.py [--tarball PATH]

It installs the version pinned in `tools/house_format/quarto.toml` into `vendor/quarto/quarto-<version>/`
(git-ignored) and prints the binary's path. With that version already installed and no `--tarball`, it does
nothing. Otherwise it takes the tarball given, or downloads the release's tarball for this platform, checks its
SHA-256 against the pin before unpacking anything, unpacks it with `tarfile`'s "data" filter (PEP 706) into a
temporary folder under `vendor/quarto/`, and moves the unpacked tree into place once `bin/quarto --version`
prints the pinned version. The Linux tarballs hold that tree in a folder `quarto-<version>/`, the macOS tarball at
its top level. On a platform not in the pin's `tested` list it prints one line to stderr saying so, and goes on. A given tarball is always checked, even when an install exists. A refusal (a digest
that differs from the pin, a platform with no row in it, a wrong version, a failed download) prints one line and
exits 1.

To render a document with the house format, copy it into a scratch folder beside a symlink `_extensions` pointing
to `tools/house_format/_extensions` (Quarto finds an extension only in an `_extensions/` folder beside the
document), and in that folder run

    <quarto> render DOC.md --to house-typst [--metadata-file F]

where `<quarto>` is the path this script prints. A metadata file's `notice` is set at the head of every page. The
starter document is `tools/house_format/sample.md`; render only a copy, since Quarto writes beside the document.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "tools" / "house_format" / "quarto.toml"
VENDOR = ROOT / "vendor" / "quarto"
INSTALL_COMMAND = ".venv/bin/python tools/quarto_setup.py"


class Refusal(Exception):
    """A refusal; its str() is the one-line message."""


def download_url(version: str, platform: str) -> str:
    """The release tarball's address, by the release's naming pattern."""
    return (
        f"https://github.com/quarto-dev/quarto-cli/releases/download/v{version}/quarto-{version}-{platform}.tar.gz"
    )


def current_platform() -> str:
    """This machine's platform, as the release names its tarballs and the pin names its rows."""
    system, machine = platform.system(), platform.machine().lower()
    arch = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine, machine)
    if system == "Darwin":
        return "macos"
    return f"{system.lower()}-{arch}"


def _pin() -> tuple[str, dict[str, str], list[str]]:
    data = tomllib.loads(PIN.read_text(encoding="utf-8"))
    version = str(data["version"])
    table: dict[str, object] = data["sha256"]
    tested: list[object] = data["tested"]
    return version, {str(k): str(v) for k, v in table.items()}, [str(p) for p in tested]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def install(dest: Path, tarball: Path | None = None) -> Path:
    """Install the pinned Quarto under dest and return its binary, dest/quarto-<version>/bin/quarto."""
    version, digests, tested = _pin()
    plat = current_platform()
    if plat not in digests:
        raise Refusal(f"refused: platform {plat} has no row in {PIN}; pinned platforms: {', '.join(sorted(digests))}")
    if plat not in tested:
        print(f"note: the install of Quarto {version} is untested on {plat}", file=sys.stderr)
    target = dest / f"quarto-{version}"
    exe = target / "bin" / "quarto"
    if tarball is None and exe.is_file():
        return exe
    dest.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".quarto-setup-", dir=dest))
    try:
        if tarball is None:
            url = download_url(version, plat)
            tarball = work / "quarto.tar.gz"
            try:
                with urllib.request.urlopen(url) as response, tarball.open("wb") as out:
                    shutil.copyfileobj(response, out, 1 << 20)
            except (urllib.error.URLError, OSError) as e:
                raise Refusal(f"refused: download of {url} failed: {e}") from None
        actual = _sha256(tarball)
        if actual != digests[plat]:
            raise Refusal(
                f"refused: {tarball} has SHA-256 {actual}, but {PIN} pins {digests[plat]} for {plat}"
            )
        if exe.is_file():
            return exe
        unpacked = work / "unpacked"
        with tarfile.open(tarball) as tf:
            tf.extractall(unpacked, filter="data")
        new = unpacked / f"quarto-{version}"
        if not new.is_dir():
            new = unpacked
        got = subprocess.run([str(new / "bin" / "quarto"), "--version"], capture_output=True, text=True)
        if got.returncode != 0 or got.stdout.strip() != version:
            printed = " ".join((got.stdout + got.stderr).split())
            raise Refusal(f"refused: the unpacked bin/quarto --version printed {printed!r}, not the pinned {version}")
        os.rename(new, target)
        return exe
    finally:
        shutil.rmtree(work, ignore_errors=True)


def binary() -> Path:
    """The installed binary, vendor/quarto/quarto-<version>/bin/quarto under the repository root."""
    version, _, _ = _pin()
    exe = VENDOR / f"quarto-{version}" / "bin" / "quarto"
    if not exe.is_file():
        raise Refusal(f"Quarto {version} is not installed; run {INSTALL_COMMAND} from the repository root")
    return exe


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the pinned Quarto into vendor/quarto.")
    parser.add_argument("--tarball", type=Path, help="a local copy of the release tarball, checked against the pin")
    args = parser.parse_args()
    tarball: Path | None = args.tarball
    try:
        print(install(VENDOR, tarball))
    except Refusal as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
