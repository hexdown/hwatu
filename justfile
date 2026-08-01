venv_bin := ".venv/bin"

# list available recipes
default:
    @just --list

# create venv and install dependencies
init:
    python3 -m venv .venv
    {{venv_bin}}/pip install -e '.[dev]'

# open the karnak orchard and hear it speak
run:
    @{{venv_bin}}/python3 tests/demo.py

# seed the karnak genesis into a filestore at the given path
seed path:
    @{{venv_bin}}/python3 tests/seed.py {{path}}

# start a python repl inside the virtual environment
repl:
    {{venv_bin}}/python3

# autoformat code
format:
    {{venv_bin}}/ruff format .
    {{venv_bin}}/ruff check --fix .

# run static type checking
typecheck:
    {{venv_bin}}/ty check hwatu tests

# run unit tests
test:
    {{venv_bin}}/pytest -vv -s

# run all validation checks
validate: && typecheck test
    {{venv_bin}}/ruff format --check .
    {{venv_bin}}/ruff check .

# remove venv dir and other build artifacts
clean:
    @rm -rf .venv
    @rm -rf hwatu.egg-info
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @rm -rf hwatu/__pycache__
    @rm -rf tests/__pycache__
