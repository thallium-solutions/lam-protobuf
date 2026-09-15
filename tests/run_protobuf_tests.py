#!/usr/bin/env python3
# Copyright 2026 Thallium Solutions di Busconi Alessandro.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


LIB_ROOT = Path(__file__).resolve().parents[1]
COMPILER = "lamc"
MIN_COMPILER_VERSION = (1, 16, 0)
PACKAGE_PATH = Path("@lam") / "protobuf"
VERSION_RE = re.compile(
    r"^(?:lamc\s+)?v?(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def _check_compiler() -> bool:
    try:
        proc = subprocess.run(
            [COMPILER, "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        print(f"Error: {COMPILER} is not installed or not available on PATH.", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print(f"Error: {COMPILER} version check timed out.", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"Error: unable to run {COMPILER}: {exc}.", file=sys.stderr)
        return False

    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        message = f"Error: unable to check {COMPILER} version"
        if detail:
            message += f": {detail}"
        print(message + ".", file=sys.stderr)
        return False

    version_text = proc.stdout.strip()
    match = VERSION_RE.fullmatch(version_text)
    if not match:
        print(f"Error: {COMPILER} returned an invalid version: {version_text!r}.", file=sys.stderr)
        return False

    version = tuple(int(part) for part in match.groups()[:3])
    prerelease = match.group(4)
    if version < MIN_COMPILER_VERSION or (version == MIN_COMPILER_VERSION and prerelease):
        required = ".".join(str(part) for part in MIN_COMPILER_VERSION)
        print(
            f"Error: {COMPILER} {version_text} is incompatible; version >= {required} is required.",
            file=sys.stderr,
        )
        return False
    return True


def _expectations(source: str) -> list[str]:
    return [
        match.group(1).strip()
        for line in source.splitlines()
        if (match := re.match(r"^\s*#\s*expect:\s*(.*)$", line))
    ]


def _details(proc: subprocess.CompletedProcess[str]) -> str:
    parts = []
    if proc.stdout.strip():
        parts.append("stdout:\n" + proc.stdout.strip())
    if proc.stderr.strip():
        parts.append("stderr:\n" + proc.stderr.strip())
    return "\n".join(parts) or "(no output)"


def _run_case(path: Path) -> tuple[bool, str]:
    source = path.read_text(encoding="utf-8")
    expected = _expectations(source)

    with tempfile.TemporaryDirectory(prefix="lam_protobuf_consumer_") as tmp:
        root = Path(tmp)
        extlibs = root / "extlibs"
        package = extlibs / PACKAGE_PATH
        package.parent.mkdir(parents=True)
        package.symlink_to(LIB_ROOT, target_is_directory=True)

        consumer_source = root / "main.lam"
        consumer_source.write_text(source, encoding="utf-8")
        binary = root / "test_binary"
        command = [
            COMPILER,
            str(consumer_source),
            "--extlibs",
            str(extlibs),
            "--no-cache",
            "-o",
            str(binary),
        ]

        try:
            compile_proc = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=240,
            )
        except subprocess.TimeoutExpired:
            return False, "COMPILE FAIL: timed out after 240 seconds"
        except OSError as exc:
            return False, f"COMPILE FAIL: unable to run {COMPILER}: {exc}"

        if compile_proc.returncode != 0:
            return False, f"COMPILE FAIL ({compile_proc.returncode}):\n{_details(compile_proc)}"

        try:
            run_proc = subprocess.run(
                [str(binary)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            return False, "RUN FAIL: timed out after 60 seconds"
        except OSError as exc:
            return False, f"RUN FAIL: unable to execute test binary: {exc}"

        if run_proc.returncode != 0:
            return False, f"RUN FAIL ({run_proc.returncode}):\n{_details(run_proc)}"

        actual = run_proc.stdout.rstrip("\n")
        expected_text = "\n".join(expected).strip()
        if expected and actual != expected_text:
            return False, (
                "OUTPUT MISMATCH:\n"
                f"  expected: {expected_text!r}\n"
                f"  actual:   {actual!r}\n"
                f"  stderr:   {run_proc.stderr.strip()!r}"
            )
        return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="@lam/protobuf package tests")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not _check_compiler():
        return 1

    cases = sorted((LIB_ROOT / "tests").glob("test_*.lam"))
    if not cases:
        print("Error: no @lam/protobuf test cases found.", file=sys.stderr)
        return 1

    failures: list[tuple[Path, str]] = []
    print(f"Running {len(cases)} @lam/protobuf test(s)...\n")
    for case in cases:
        ok, message = _run_case(case)
        relative = case.relative_to(LIB_ROOT)
        print(f"  {'PASS' if ok else 'FAIL'}  {relative}")
        if not ok:
            failures.append((relative, message))
            if args.verbose:
                for line in message.splitlines():
                    print(f"        {line}")

    passed = len(cases) - len(failures)
    print(f"\n@lam/protobuf results: {passed} passed, {len(failures)} failed, {len(cases)} total")
    if failures and not args.verbose:
        for relative, message in failures:
            print(f"  FAIL  {relative}")
            for line in message.splitlines()[:8]:
                print(f"        {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
