# Brief: the audit referee, round 1, on the fast draft

A reviewer of `notes/fast_estimate.md` 1.3.2, dispatched as the `audit-referee` agent (`.claude/agents/audit-referee.md`). The coordinator fills each `[[...]]` from the author's return, drops an item marked optional where it does not apply, and sends only the text below the line `=== BRIEF ===` as the task. What is the same at every dispatch is in the definition: this brief's former charge (items 6 to 9), its rules (items 10 to 15), the welfare paragraph, and the simplicity paragraphs of `notes/briefs/simplicity.md`.

=== BRIEF ===

This is round 1 of review of the fast draft of the case [[case]], on the git branch main. The draft was written by notes/fast_estimate.md, of which you are the audit referee of 2.2: every effect estimated by hand as a product of a few factors, with no model in code. Nothing you say is acted on while the fast draft is made; afterwards an editor turns the reviews into one decision letter, and the author revises against it by notes/peer_review_trial.md.

The submission is [[the case in one sentence: the action, against what]], all in cases/[[case]]/:
1. documents/technical_note.md, the paper, with documents/executive_summary.md.
2. requirements.md, CASE.md and design.md; baseline/, the facts records of the world today.
3. effects/pooled.md; estimates/, the estimators' files with their arithmetic; estimates.toml ([[n]] effects); sources.toml ([[n]] entries, [[m]] stored in sources/).
4. The total tool's output, from `.venv/bin/python tools/estimate_total.py cases/[[case]]/estimates.toml` on commit [[commit]]. [[Optional: the earlier work the case ports, read-only at its path; the author reports its reconciliation with it as follows, from its return.]]

5. Where to start. Read each estimator's notes to the author, in estimates/, first. Take each factor's mean early, from `factors` in the total tool's results (the mean of its draws): an effect's middle and its expected value can differ twofold. Take each headline mean from the draws file your rerun writes (`--draws`) and check the tool's arithmetic against it; check that each factor's form is the one `notes/factor_forms.md` gives for its kind of quantity, and for an effect that can change sign check its corners and that the documents give its chance of each sign. Where the author assembled the table from the estimators' blocks ([[the assembly note, such as estimates/README.md, or none]]), first compare each factor of the table with its estimator's block and name the rule of that note that explains each change; a change no rule explains is a finding.
6. The sources the author says it could read only in part, or could not store: [[from its return]].
7. Write your report to cases/[[case]]/review/fast_audit.md, findings A1 onward, the size check and the simplifications first. You are blind to the other reviewers until round 2.
7.1 [[Optional, where the case has an earlier milestone or version: the record of its closed points, the comment resolution matrix that opens review/[[the last response letter]], with the commit its last ruling accepted, [[commit]]; read it by your definition's rule 1.]]
8. Your return: the verdict, the three gravest findings one line each, and the report's path. You will be resumed with your memory for round 2, so keep your notes in the report.
