# 11.4 The compliance matrix

Part of section 11 of the `scope-case` skill, read when the user supplies a document (`SKILL.md` 0.6) and again when its last two columns are filled (0.10.2); its numbers continue those of `SKILL.md`. A proposal writer's tool, pre-requirements traceability (`gotel_1994_traceability`) applied to a document: each requirement a governing document states, in a row, against where the analysis meets it.

11.4.1 The document is stored as a source at its level, text and original, as every source is (`cases/README.md`): an analysis's in `cases/<case>/sources/<key>/`, an organization's in `organizations/<org>/sources/<key>/`, with its entry in that level's `sources.toml`. Its matrix is `matrix.md` beside its text.

11.4.2 A helper agent reads the stored text and writes the matrix, one row for each requirement the document states (a "must", "shall", "should" or "is required", or a setting it fixes, such as a discount rate), quoting and deciding nothing. Its prompt gives it the text's path, the matrix's path, the columns below, and the numbers and names of the guide's topics (`topic_guide.md`); it fills the first four columns and leaves the last two empty.

| # | Document, edition, section | The requirement, verbatim | Binding or advisory | Topic of the guide, or "not in the guide" | Where the analysis meets it | Status |
|---|---|---|---|---|---|---|

11.4.3 The session checks each quote against the stored text (a search of `text.txt` finds it word for word) before relying on it, and says back its reading of each row that bears on the analysis. A binding row on a topic of the guide settles that topic as fixed (0.7.2); a row marked "not in the guide" that bears on the analysis is raised in the conversation; and a row the user decides becomes a requirement.

11.4.4 After the read-back the session fills the last two columns: the requirement that meets the row, or "not met" and why; and the status, met, not met, open, or not applicable with the user's reason. The matrix, the stored document and its `sources.toml` entry are committed with the requirements (0.10.3).
