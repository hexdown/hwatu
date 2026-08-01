"""seed the karnak genesis into a filestore: `just seed <path>`.

aim it at the corpus repo to grow the golden store:
`just seed ../corpus/hexdown/karnak`
"""

import sys

import genesis

from hwatu import store


def main(path: str) -> None:
    backing = store.FileStore(path)
    genesis.seed(backing)
    records = sum(
        1 for table in ("tills", "flushes") for _ in backing.scan(table)
    )
    faces = sum(1 for _ in backing.scan("faces"))
    print(f"seeded karnak at {path}: {records} records, {faces} faces")


if __name__ == "__main__":
    main(sys.argv[1])
