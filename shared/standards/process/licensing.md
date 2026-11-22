# Licensing what a project makes

Who owns what every project makes, under which licence each kind of file is offered, and how that is stated so a person and a tool can both read it. The owner's approval, 2026-11-02 (the owner's message of 2026-11-02): "ok do your recommended 10.6 and 12.4"; the licensing scheme is the seat's recommendation, which he approved, after the discussion recorded in the author's shared coordinator-reading history 10.11 and 10.12.

## 1. The holder and the author

1.1 Max Welfare Inc. holds the copyright in what the projects make: work made within the scope of employment is a work made for hire, owned by the employer (17 U.S.C. § 201(b); *CCNV v. Reid*, 1989). An optional confirmatory assignment removes any doubt for work made before or outside that scope; as in most open-source projects, the licence files alone state the terms. Copyright lines read `Max Welfare Inc.`.

1.2 Richard Bruns is named as author wherever authorship is stated: `CITATION.cff`, papers, course material. Holder and author are separate fields; the author's credit does not depend on who holds the copyright.

1.3 Much of the code and text is written by AI under his direction; copyright in those parts may be thin (U.S. Copyright Office 2025, Part 2). The licence still states what users may do with whatever rights exist.

## 2. The licence of each kind of file

2.1 Code: MIT. In a harness repository (the shared folder once released), everything the holder owns is MIT, prompts, agent definitions, workflows, configuration and standards included, one licence for the repository.

2.2 Text in a project repository (designs, research notes, papers, course material, READMEs): CC BY 4.0, so the author's name travels with the teaching material.

2.3 Data the project made and its results (inputs, the source records in `sources.toml`, computed data, results, lineage crates): CC0 1.0. Facts carry little copyright, CC BY on data stacks attributions on every reuse, and some repositories take only CC0 (Dryad's rationale); credit comes from the citation norm and `CITATION.cff`.

2.4 Third-party material (stored copies of sources, extracts of others' data, seed sets): not licensed by the holder, and tracked in the project's private repository, save a file over GitHub's 50 MB warning, which stays local and is named in `.gitignore` (the owner, ieq-modeling register the owner's message of 2026-11-07: "yes to most files but leave out anything that would make github mad at me"; the 50 MB threshold, the `.gitignore` rule and `LicenseRef-third-party` are the seat's). It keeps its owner's terms, named under the owner's SPDX identifier where the owner licenses it openly, otherwise as `LicenseRef-third-party`, and each source's `licence` field in its index says what is known. A public release carries it only where its terms allow redistribution (the AEA: a package contains only data that can be redistributed).

This follows Stodden's Reproducible Research Standard (2009) and the AEA Data Editor's licensing guidance, which pairs a permissive code licence with CC BY 4.0 and names CC0 as the more liberal option; it departs from the AEA's default in putting data under CC0 and code under MIT rather than BSD-3, by the seat's recommendation, which the owner approved (the owner's message of 2026-11-02; his stated aim was to release the harness "as a public service anyway", the owner's message of 2026-11-02; the CC0 and MIT choice and its reason are the seat's) (any open-source licence is acceptable to the AEA).

## 3. How it is stated

3.1 The REUSE specification 3.3: the licence texts from the SPDX list in `LICENSES/<identifier>.txt`; a `REUSE.toml` at the root mapping paths to licence and copyright, in which the last matching `[[annotations]]` table wins, so it runs from the default to the exceptions.

3.2 A `LICENSE.md` at the root saying the same in plain words, in the AEA's dual-licence form.

3.3 A `CITATION.cff` (Citation File Format 1.2.0) naming the author and the holder's licence for the code.

3.4 The lineage crate (`ro-crate-metadata.json`, the cost-benefit project's `tools/lineage.py`) carries the licence of the crate and of each file in it.

## 4. Before a public release

4.1 `reuse lint` passes, and every third-party file is either removed or confirmed redistributable. A session runs the checker from uv's cache, which the owner filled on 2026-11-02: `UV_TOOL_DIR=$TMPDIR/uvtools .venv/bin/uvx --offline reuse lint` at the project's root.

4.2 Publishing a repository publishes its history: a public repository starts from a cleaned copy of the tree, leaving out the owner's registers, welfare logs, transcript notes and anything about clients.

4.3 Before the first push of a public copy, one reader who has seen neither the scan's result nor the builder's account reads every text file in it whole, and uses grep across the copy as a second net for anything found once. A scan for the owner's private patterns is the cheap first net: it matches names, and a sentence can describe private work without one. The read is of every file, not of the differences, since a file the update did not change is not in them, and it comes before the push because a push cannot be recalled.

## Sources

Stodden 2009 (`stodden_2009_enabling`), the AEA Data Editor's licensing guidance (`aea_licensing_guidance`), REUSE 3.3 (`reuse_spec_3_3`), Dryad on CC0 (`dryad_2011_cc0`), the Copyright Office's 2025 report (`usco_2025_ai_part2`), 17 U.S.C. § 201 (`usc_17_201`) and *CCNV v. Reid* (`ccnv_v_reid_1989`), all in `library/refs.toml`.
