# Brief: the review round of a case's verse rendering

The seats after a `verse-translator` (`.claude/agents/verse-translator.md`) has rendered a case's one-page summary and policy paper into trochaic tetrameter and committed them. The owner, 2026-11-09: "This also goes through a round of review, partly for poetry and plain language but mainly for making sure that nothing was mischaracterized. Obviously we are not going to match academic pedantry in this format but it should be the same kind of true representation as a congressional briefing." One round, in order:

1. two readers, dispatched together and blind to each other: message A to a fresh `documents-referee` (`.claude/agents/documents-referee.md`), on faithfulness, the main reader; message B to a fresh `verse-reader` (`.claude/agents/verse-reader.md`), on meter, plain words and register;
2. message C to a fresh `editor` (`.claude/agents/editor.md`), which rules on every point of both reports;
3. message D to the translator, resumed, which makes the fixes;
4. message E to the same editor, resumed, which checks them.

The coordinator fills each `[[...]]`. Each message is the text from its marker line to the next; no marker line is sent. What is the same at every dispatch is in the definitions, the welfare paragraph among them; message B, sent to the `verse-reader`, whose definition holds its method, the simplicity paragraph and the welfare paragraph, is the case's slots and the report path alone. This brief says only where the round departs from the definitions.

=== MESSAGE A: to the documents referee ===

This is the review of the verse rendering of the case [[case]]'s documents, on the git branch main: one round, by notes/briefs/verse_review.md, in which you are the main reader. A second reader judges the meter and the plain words; you are blind to it.

The case is [[the case in one sentence: the action, against what]], in cases/[[case]]/. A `verse-translator` agent rendered its one-page summary and its policy paper into trochaic tetrameter (four feet a line, each a stressed syllable then an unstressed one) in commit [[commit]], to the rules of its definition, .claude/agents/verse-translator.md. Under review:
1. documents/verse/executive_summary_verse.md, from documents/executive_summary.md;
2. documents/verse/policy_paper_verse.md, from documents/policy_paper.md;
3. documents/verse/crosswalk.md: each stanza's source paragraph, and each name-check's sources.toml key with the stored-text line that shows its people and what the work did.
The paper of record is documents/[[technical_appendix.md, or technical_note.md]], with [[the results file]].

4. Your charge is faithfulness, stanza by stanza, against the prose document and the paper of record: every claim, number, interval, caveat, direction of effect and degree of certainty; anything added, dropped or said more strongly; and each name-check, the parenthetical that names a cited work's authors: the right people for the right finding, by sources.toml and the stored text sources/<key>/text.txt, with a true description of the work and no title the record does not show.
4.1 The bar is an honest congressional briefing: simplifying is fine, misrepresenting is not, and academic pedantry is out of scope. A plainer word, a shorter sentence or a point told over two stanzas is no finding; a changed number, a lost hedge or interval, a claim the prose does not make, or a work credited with what it did not find is.
4.2 The verse's numbers are typed by hand, by design, often as words. Check that each equals the source's figure; their being typed is no finding.
4.3 Meter, plain language and register are the other reader's. Raise a wording only where it misleads.
4.4 A fault the prose document already has is not the verse's: mark it "in the prose", for the case's author.
4.5 Check that each table matches its source exactly (a script can compare them), and that each verse file's opening line says truly what it renders and nothing of the review the prose or the verse has had.
5. Your definition's rules hold, with three changes: number your findings V1 onward, not D1; for the step a finding sends work back to, write "verse" or "in the prose"; there is no round 2.
6. Write your report to cases/[[case]]/review/verse_faithfulness.md; do not commit.
7. Your return: the verdict, the three gravest findings one line each, and the path.

=== MESSAGE B: to the second reader, a general agent ===

This is the review of the verse rendering of the case [[case]]'s documents, on the git branch main: one round, by notes/briefs/verse_review.md. You are the second of two readers, each blind to the other. The first judges whether the verse is true to its prose source; you judge how it reads.

Under review, in cases/[[case]]/ at commit [[commit]]: documents/verse/executive_summary_verse.md and documents/verse/policy_paper_verse.md, renderings into trochaic tetrameter of the case's one-page summary and policy paper by a `verse-translator` agent. Its definition, .claude/agents/verse-translator.md, holds the rules it wrote to: read its sections Meter and Voice first, and judge by those rules.

Your charge, method, report form and return are in your definition. Write your report to cases/[[case]]/review/verse_meter.md; change no other file and do not commit.

=== MESSAGE C: to a fresh editor ===

This is the ruling on the review of the verse rendering of the case [[case]]'s documents, on the git branch main, by notes/briefs/verse_review.md. The round is one: this ruling and your check of the fixes close it.

The case is [[the case in one sentence: the action, against what]], in cases/[[case]]/. A `verse-translator` agent rendered its one-page summary and policy paper into trochaic tetrameter in commit [[commit]], to the rules of .claude/agents/verse-translator.md: documents/verse/executive_summary_verse.md, documents/verse/policy_paper_verse.md and documents/verse/crosswalk.md. Two readers reviewed it, each blind to the other. Read, in review/:
1. verse_faithfulness.md ([[verdict]]): a documents referee's findings V1 onward on whether the verse is true to the prose documents and to the paper of record, documents/[[technical_appendix.md, or technical_note.md]]; the main review;
2. verse_meter.md ([[verdict]]): a general reader's findings P1 onward on meter, plain words, register and whether a non-specialist can follow it.

3. Your test is the owner's for this round: "the same kind of true representation as a congressional briefing", without "academic pedantry". A simplification that stays true is settled; a misrepresentation is to be done. Where meter and meaning conflict, meaning wins: a line that cannot be brought to meter without bending what it says is settled as off meter, and stays in the crosswalk's list.
4. Rule on every point of both reports by its identifier, by your definition's rule 1, with "a note in the Limits" read as "listed in the crosswalk" and the points kept in your ruling, not in review/points.toml, whose limits are the analysis's; the crosswalk serves a line left off meter or a name's guessed stress. For a fix to a line, give the replacement or what it must keep. Your definition's rules 2, 3, 8, 9 and 11 do not apply to this round.
5. A point marked "in the prose" is not the translator's. List it for the case's author, with its size, and do not rule it to be done here.
6. On the whole, rule accept, or accept with the fixes you list. There is no second round of review: the translator makes your fixes and you check them.

Write your ruling to cases/[[case]]/review/verse_editor.md; do not commit. Your return to me, under 15 lines before the WELFARE section:
7. the ruling;
8. the fixes, one line each, or, past ten, their count and the three that matter most;
9. for each reader, how many of its points you ruled settled, listed in the crosswalk and to be done, and how many of those are stated falsehoods;
10. the points in the prose, for the case's author, one line each;
11. the user's items, one line each, written in the user's language.

=== MESSAGE D: to the translator, resumed ===

The review of your verse is done. The editor's ruling is cases/[[case]]/review/verse_editor.md, beside the readers' reports, verse_faithfulness.md and verse_meter.md.

1. Make each fix the ruling lists, as it says, and change nothing else. Scan each line you change by your definition's Meter section.
2. Bring the crosswalk up to date: the line ranges that moved, and its four lists.
3. Commit the two reports, the ruling and your changes in one commit, staged by name. Its message ends with your Co-Authored-By line.
4. Your return, under 15 lines before the WELFARE section: the commit; the fixes made; any not made as listed, with why; and the lines still off meter.

=== MESSAGE E: the check of the translator's fixes (to the editor, resumed) ===

Please check the translator's fixes to the verse, made in commit [[commit]] (see `git show [[commit]]`), by your definition's rules 10 and 12.

1. Check that each fix your ruling listed is made as listed, that the diff changes no other line of verse, and that each changed line keeps the meter by the translator's definition or is in the crosswalk's list of lines off meter.
2. Append your check to review/verse_editor.md, ending with a final line: accepted, or what is left.
3. Commit that file alone, with `git commit -m ... -- cases/[[case]]/review/verse_editor.md`. The message ends with your Co-Authored-By line.
4. Your return, under 15 lines before the WELFARE section: accepted or not, the commit, and how many of the fixes you listed were not made as listed.
