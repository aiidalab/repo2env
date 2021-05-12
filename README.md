# repo2env

Determine the environment specification for a given (app) repository.

This tool parses an (app) repository and determines requirements similar to [repo2docker](https://github.com/jupyterhub/repo2docker).
But instead of generating a docker image it returns a specification that can then be used to build the environment.

## Installation

The easiest way to install this tool is either directly with pip:
```bash
~ $ pip install git+https://github.com/aiidalab/repo2env.git
```

Or clone the repository first and then install:
```bash
~ $ git clone https://github.com/aiidalab/repo2env.git
~ $ cd repo2env/
~/repo2env $ pip install .
```

## Usage

Use the `repo2env` command to parse the environment of a local or remote (app) repository:

For a local repository, just provide the path:
```bash
~ $ repo2env /path/aiidalab-hello-world/
{"python_requirements": ["aiidalab>=20.02.0b2"]}
```

For a remote repository, provide a [PEP 508](https://www.python.org/dev/peps/pep-0508/) compliant URL, for example:
```bash
~ $ repo2env git+https://github.com/aiidalab/aiidalab-hello-world.git@v1.0.0
{"python_requirements": ["aiidalab>=20.02.0b2"]}
```

The output is JSON-formatted and can then be used for further processing.

Tip: Use [jq](https://stedolan.github.io/jq/) to generate pretty-printed output for manual inspection:
```bash
$ repo2env ~/local/aiidalab/aiidalab-hello-world/ | jq .
{
  "python_requirements": [
    "aiidalab>=20.02.0b2"
  ]
}
```

## What is parsed

 - `setup.cfg`: If present, the `options.install_requires` list is parsed into `python_requirements`.
 - `requirements.txt` Is parsed into `python_requirements` if present and `setup.cfg` is not present.

## Acknowledgements

This work is supported by the [MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>) funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>),
as well as by
the MARKETPLACE project funded by [Horizon 2020](https://ec.europa.eu/programmes/horizon2020/) under the H2020-NMBP-25-2017 call (Grant No. 760173).
