# -*- coding: utf-8 -*-
"""App environment specification

The specification is used to describe a reproducible environment for a
specific app, similar to the Reproducible Environment Specification (REES) [1]

[1] https://repo2docker.readthedocs.io/en/latest/specification.html

The following configuration files are recognized:

.. glossary::

    requirements.txt
        Describes a list of pip-installable packages that must be present in
        the Python environment that is used to execute the app.

    jupyter-requirements.txt
        Describes a list of pip-installable packages that must be present in
        the Python environment that is used to run Jupyter.
"""
from configparser import ConfigParser
from dataclasses import dataclass
from dataclasses import field
from typing import List


__all__ = [
    "Environment",
]


@dataclass
class Environment:
    """App environment specification.

    This dataclass contains the specification of an app environment and can be
    used to scan an existing environment configuration from a given path and to
    detect whether a given environment is meeting the specification.
    """

    python_requirements: List[str] = field(default_factory=list)

    _FILES = (
        "jupyter-requirements.txt",
        "requirements.txt",
    )

    @staticmethod
    def _scan(path):
        def _parse_reqs(requirements):
            for line in (line.strip() for line in requirements.splitlines()):
                if line and not line.startswith("#"):
                    yield line

        def _parse_setup_cfg(setup_cfg):
            cfg = ConfigParser()
            cfg.read_string(setup_cfg)
            return cfg["options"].get("install_requires", [])

        try:
            yield "python_requirements", list(
                _parse_reqs(_parse_setup_cfg(path.joinpath("setup.cfg").read_text()))
            )
        except (FileNotFoundError, KeyError):
            try:
                yield "python_requirements", list(
                    _parse_reqs(path.joinpath("requirements.txt").read_text())
                )
            except FileNotFoundError:
                pass

    @classmethod
    def scan(cls, root):
        """Scan the root path and determine the environment specification."""
        return cls(**dict(cls._scan(root)))
