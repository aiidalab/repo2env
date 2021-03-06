import tarfile
import tempfile
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from urllib.parse import urldefrag
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import dulwich
import requests

from repo2env.git_util import GitPath
from repo2env.git_util import GitRepo


def _this_or_only_subdir(path):
    members = list(path.iterdir())
    return members[0] if len(members) == 1 and members[0].is_dir() else path


@contextmanager
def _fetch_from_path(path):
    if path.is_dir():
        yield path
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with tarfile.open(fileobj=BytesIO(path.read_bytes())) as tar_file:
                tar_file.extractall(path=tmp_dir)
                yield _this_or_only_subdir(Path(tmp_dir))


@contextmanager
def _fetch_from_https(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    content = response.content
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()
        with _fetch_from_path(Path(tmp_file.name)) as path:
            yield path


def _parse_git_url(git_url):
    path = urldefrag(git_url).fragment
    if "@" in git_url:
        url, rev = urldefrag(git_url).url.rsplit("@", 1)
    else:
        url, rev = urldefrag(git_url).url, None
    return url, (rev or "HEAD"), path


@contextmanager
def _fetch_from_git_https(git_url):
    url, rev, path = _parse_git_url(git_url)

    with tempfile.TemporaryDirectory() as tmp_dir:
        repo = GitRepo.clone_from_url(url, tmp_dir)
        git_path = GitPath(repo.path, repo.ref_from_rev(rev)).joinpath(path)
        with _fetch_from_path(git_path) as path:
            yield path


@contextmanager
def _fetch_from_git_local(git_url):
    url, rev, path = _parse_git_url(git_url)

    try:
        repo = GitRepo(urlsplit(url).path)
    except dulwich.errors.NotGitRepository as error:
        raise RuntimeError(
            f"{error}"
            + (" Did you use a relative path?" if urlsplit(url).netloc else "")
        )

    git_path = GitPath(repo.path, repo.ref_from_rev(rev)).joinpath(path)
    with _fetch_from_path(git_path) as path:
        yield path


@contextmanager
def fetch_from_url(url):
    ps = urlsplit(url)

    if ps.scheme in ("", "file"):  # on the local file system
        try:
            with _fetch_from_path(Path(ps.path)) as path:
                yield path
        except FileNotFoundError as error:
            raise RuntimeError(
                f"{error}" + (" Did you use a relative path?" if ps.netloc else "")
            )

    elif ps.scheme == "https":  # access archive via https
        with _fetch_from_https(url) as path:
            yield path

    elif ps.scheme == "git+https":  # clone git repository via https
        with _fetch_from_git_https(urlunsplit(ps._replace(scheme="https"))) as path:
            yield path

    elif ps.scheme == "git+file":  # parse local git repository
        with _fetch_from_git_local(urlunsplit(ps._replace(scheme=""))) as path:
            yield path

    else:  # unknown scheme
        raise ValueError(f"Unsupported scheme: {ps.scheme}.")
