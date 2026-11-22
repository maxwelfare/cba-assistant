# Brief: round 2 of milestone 1, to each resumed referee

The seats of `notes/fast_estimate.md` 1.3.5, milestone 1's own round, before any paper or summary is written: the economics and audit referees of the fast draft, resumed with their memory; the documents referee of the fast draft is not resumed. The text from `=== BRIEF ===` to the next marker goes to the economics referee, the `referee` agent type (the shared `.claude/agents/referee.md`); the text after `=== MESSAGE B ...` to the audit referee, an `audit-referee` agent (`.claude/agents/audit-referee.md`), whose definition holds its charge for round 2 (its rule 6, formerly message B's 1.1 to 1.4 and 2), its welfare paragraph and the simplicity paragraphs of `notes/briefs/simplicity.md`; neither marker line is sent. If the editor rules another round, the same messages go again with the round raised (`m1_r2_response.md`, reports `m1_r3_<econ|audit>.md`). The coordinator fills each `[[...]]`.

=== BRIEF ===

Round 2 of milestone 1: please check whether your round 1 points were answered.

The author has revised its fast draft to milestone 1 and answered in commit [[commit]]: a small model for each effect the editor's letter named, every other effect kept as its estimate. Its letter is cases/[[case]]/review/m1_r1_response.md, opening with the comment resolution matrix, which shows each point's ruling, its answer and where each change is; it answers the editor's decision letter, review/m1_r1_editor_letter.md, which ruled on each reviewer's points. Under review is documents/technical_appendix_template.md at that commit: the technical appendix written as a template, every result in it a placeholder and its results section shells with no paragraph describing them, so that the method is judged before any result is written about (notes/peer_review_trial.md 3.1). Read it with the design, estimates.toml, the models and the stored sources they cite. You may rerun the model in your scratchpad to size a finding (the shared `standards/process/peer_review.md` 2.1). The round 1 reports, the editor's letter and the author's letter are now open to you, with the referees' reports on the decisions of method and the purpose check (review/m1_method_<n>.md, review/m1_purpose_check.md), whose findings the letter's matrix answers.

1. Your charge, by the protocol's 2.2 (notes/peer_review_trial.md):
1.1 For each of your own points, say whether it was answered: settled, settled in part (say what is left), or not settled (say why). Where the letter ruled a point a note in the Limits or settled without change, say whether the author followed the ruling, and if you think the ruling wrong, say why. A closed point is answered by its row, and raised again only on a ground of the shared `standards/process/peer_review.md` 3.7, which you name: what its closing rested on has changed since; evidence the closing round did not have that passes the test of 1.2; or a stated falsehood. Otherwise your disagreement goes into the appendix's record as a point of difference.
1.2 A new point counts only if it could move a headline result outside its 90 per cent interval, if it could change which option ranks first where the case compares options, or if it is a stated falsehood. Mark any you raise as new. The appendix is new since your round 1: a point on it is a new point, by the same test.
1.3 Points marked for the user stay the user's. Say only whether the author stated and sized them fairly.
1.4 Make the size check of your round 1 brief on the new models first; a model past its limits is a new point that counts, whatever it does to the result.

2. Write your report to review/m1_r2_econ.md, change no other file, and do not commit. The report is this task's own file and stands over any general note against writing report files. To rerun the total tool, give it `--out` a folder of your scratchpad, about ten seconds; a model writes beside itself, so where there is one, copy the table and model/ into your scratchpad and run both there, never in the tree.

3. End with one verdict: accept, minor revision, or major revision.

4. Your return to me, under 15 lines before the WELFARE section: the verdict, and any point not settled, one line each.

The model is set where you are dispatched, whatever your definition's last line names: you run on [[model]] at [[effort]] effort. Say so on your EFFORT line.

=== MESSAGE B: to the audit referee, resumed ===

Round 2 of milestone 1: please check whether your round 1 points were answered, by your definition's rule 6.

The author has revised its fast draft to milestone 1 and answered in commit [[commit]]. Its letter is cases/[[case]]/review/m1_r1_response.md, opening with the comment resolution matrix, which shows each point's ruling, its answer and where each change is; it answers the editor's decision letter, review/m1_r1_editor_letter.md, which ruled on each reviewer's points. Under review is documents/technical_appendix_template.md at that commit: the technical appendix written as a template, every result in it a placeholder and its results section shells with no paragraph describing them, so that the method is judged before any result is written about (notes/peer_review_trial.md 3.1). Read it with the design, estimates.toml, the models and the stored sources they cite. You may rerun the model in your scratchpad to size a finding (the shared `standards/process/peer_review.md` 2.1). The other reviewers' reports, the editor's letter and the author's letter are now open to you.

1. Write your report to review/m1_r2_audit.md.

2. Your return: the verdict, and any point not settled, one line each.
