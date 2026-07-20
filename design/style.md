# code style

conventions for hwatu's python (and the questions hanafuda's rust will
inherit). the mechanical parts are enforced by ruff + ty via `just
validate`; these are the judgment calls:

- **absolute imports always** (`from hwatu import sips`) — modules
  shift in unexpected ways; paranoia is a feature
- **modules of functions and constants come in as modules**, referenced
  qualified inline (`sips.NEEM`, `layouts.word`) — provenance at every
  use site, collisions impossible
- **classes come in by name** (`Blossom`, `Schema`) — constructors and
  isinstance targets everywhere; capitalization carries provenance
- **rename on genuine collision** (`Layout as LayoutSpec`)
- **no single-letter names** except loop iterators — verbose and
  legible beats concise and illegible; concise and legible is best of
  all
- free functions over methods for serialize/deserialize; frozen
  dataclasses with tuple fields for anything content-addressed
