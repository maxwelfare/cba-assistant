# The typeset layout's assets

Third-party files the house format loads (tools/typeset.py links this folder into each build and names it in
Quarto's `font-paths`), stored here so a build needs no network.
Each was downloaded on 2026-11-10; their licences are recorded in the repository's `REUSE.toml`.

1. `tabler-icons/`: the Tabler icon set, version 3.41.1, under the MIT licence, copyright 2020-2026 Paweł Kuna
   (`tabler-icons/LICENSE`).
   1.1 `tabler-icons.ttf`: the outline webfont, from
   https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.41.1/dist/fonts/.
   1.2 `icons.json`: the index of 5,039 icons (name, category, tags, each style's code point), from the package
   @tabler/icons@3.41.1. `tools/typeset.py` reads the outline code points from it; `tools/icon_search.py`
   searches it.
2. `lato/`: Lato Regular, Italic, Bold, BoldItalic and Black (TrueType), by Łukasz Dziedzic, from
   https://github.com/google/fonts, folder `ofl/lato`, under the SIL Open Font License 1.1, copyright 2010-2014
   tyPoland Lukasz Dziedzic, with Reserved Font Name "Lato" (`lato/OFL.txt`; `LICENSES/OFL-1.1.txt`).
