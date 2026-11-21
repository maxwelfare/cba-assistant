# Brief: the editor of milestone 1, and its check of the fixes

The seat of `notes/fast_estimate.md` 1.3.6: the ruling on milestone 1's own round, run at every first upgrade before any paper or summary is written, and on a round of milestone 1 after a systematic review's update (`systematic_input_review.md` 10.3). Message A is the dispatch of a fresh `editor` agent (`.claude/agents/editor.md`); message B goes to the same editor, resumed, once the author has made the fixes (only if the ruling is accept with fixes). If the ruling or the check accepts once one-line fixes are made (message A, item 6.1), the author makes them by the same message as any fixes (`author_upgrade.md`, message B), no check follows, and the milestone is accepted when the author's return lists each as made. If the ruling is another round, a fresh editor gets message A with the file names raised a round (`m1_r2_response.md`, `m1_r3_<econ|audit>.md`, its ruling `m1_r3_editor.md`). The coordinator fills each `[[...]]`. Message A is the text from the line `=== BRIEF ===` to the line `=== MESSAGE B ...`, and message B the text after that line; neither marker line is sent. What is the same at every ruling is in the definition.

=== BRIEF ===

This is the ruling for milestone 1 of the case [[case]], on the git branch main. The protocol is notes/peer_review_trial.md; you are the editor of its 2.3.

The case is [[the case in one sentence: the action, against what]], in cases/[[case]]/. It began as a fast draft (notes/fast_estimate.md), every effect estimated by hand, which three reviewers commented on; another editor turned their comments into a decision letter naming the effects to model, and the author revised the draft to milestone 1 against it. Read, in its review/ folder:
1. fast_econ.md ([[verdict]]), fast_audit.md ([[verdict]]) and fast_documents.md ([[verdict]]), the round 1 reviews of the fast draft;
2. m1_r1_editor_letter.md, the decision letter ([[decision]]);
3. m1_r1_response.md, the author's letter, opening with the comment resolution matrix printed from review/points.toml, the record of review points: each point's ruling, the author's answer, where the change is, and whether the point is closed or open;
4. m1_r2_econ.md and m1_r2_audit.md, [[both verdicts]], uncommitted;
4.1 the rows of review/points.toml raised by the referees on the decisions of method (review/m1_method_<n>.md) and by the purpose check (review/m1_purpose_check.md), with the author's answers.
Read the changes too: `git diff [[the fast draft's last commit]] [[the response commit]] -- cases/[[case]]/`. The paper is documents/technical_appendix_template.md, the appendix written as a template, its results placeholders and its results section shells, since the method is ruled on before any result is written about; it states its rigor at the top, and that rigor is your test.

5. Rule on each point still open after round 2, by your definition's rules 1 to 3, and apply its rule 8, for this is a ruling after round 2.
6. On the whole, rule accept (with any fixes you list, which the author makes and you then check), accepted once one-line fixes are made (6.1), or another round.
6.1 Where everything left, at this ruling or at your check of the fixes, is fixes of one line each that need no rerun of a model and no judgement, you may rule the milestone accepted once these one-line fixes are made. List each with its file, the exact words to replace and the words to put; the author makes them and lists each in its return as made, and you make no further check. A fix that changes a number, the strength of a claim or one of the user's items is never one of these.

Write your ruling to cases/[[case]]/review/m1_r2_editor.md, and each point's ruling, state and any limit's text into its row of review/points.toml (your definition's rule 1); do not commit. Your return to me, under 15 lines before the WELFARE section:
7. the ruling;
8. the fixes for the author, one line each;
9. for each referee, how many of its points still open you ruled settled, a note and still to be done;
10. each ruling of the decision letter that a round 2 report gave cause to reopen on a ground of your definition's rule 3, by identifier and its ground, or none;
11. the user's items, one line each, written in the user's language.

=== MESSAGE B: the check of the author's fixes (sent to the resumed editor, after the author's fixes) ===

Please check the author's fixes for milestone 1, made in commit [[commit]] (see `git show [[commit]]`), by your definition's rules 9 and 10. The rulings the user or the owner has made on the case since your ruling, each with its commit, so that you can tell a fix a ruling overtook from one not made: [[the rulings, one line each with its commit; or: none]].

1. Append your check to review/m1_r2_editor.md, ending with a final line: milestone 1 accepted at [[commit]], the accepted commit, from which the run of record is made and milestone 2 is written; accepted once the one-line fixes you list are made (item 6.1 of your ruling's brief); or what is left.

2. Commit that file and the record alone, with `git commit -m ... -- cases/[[case]]/review/m1_r2_editor.md cases/[[case]]/review/points.toml`. The message ends with your Co-Authored-By line.

3. Return in under 15 lines before the WELFARE section: your final line, the commit, and how many of the fixes you listed were not made as listed.
