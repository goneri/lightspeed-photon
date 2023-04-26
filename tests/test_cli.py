#!/usr/bin/env python3
# ruff: noqa: D103, S101
from ansible_lightspeed.photon.cli import load_args


def test_load_args():
    args = load_args(".")
    assert args.path.as_posix()
