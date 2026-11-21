# Brief: the review round of a case's audience edition

By the design `notes/audience_layer.md`, as revised on 2026-11-12 to a referee's review of it. The seats after an `audience-translator` (`.claude/agents/audience-translator.md`) has re-voiced a case's one-page summary and policy paper for one audience and committed them. The owner's bound on the layer (2026-11-11, the owner's message of 2026-11-11, where his word is "ficus" for "focus"): "while still being scrupulously honest in the facts and data. But it can and should change tone, emphasis on presentation, what parts get the most focus in callout boxes". One round, in order:

1. message A to a fresh `documents-referee` (`.claude/agents/documents-referee.md`), on faithfulness and on fit to the profile;
2. message B to a fresh `editor` (`.claude/agents/editor.md`), which rules on every point;
3. message C to the translator, resumed, which makes the fixes;
4. message D to the same editor, resumed, which checks them.

Then `pdf-layout` reviews the edition's PDFs by its own definition, and the coordinator runs the commands of message A, item 4, once more. An audience edition is handed on only with the plain edition and the technical appendix beside it, the default until the owner rules (`notes/audience_layer.md` 10.2). The coordinator fills each `[[...]]`. Each message is the text from its marker line to the next; no marker line is sent. What is the same at every dispatch is in the definitions, the welfare paragraph among them. There is one reader and not two: fit to the profile is checked against the profile's own lists, and no seat plays the audience, since a model's guess at how such a reader reacts is a stereotype (`notes/audience_layer.md` 8.3).

=== MESSAGE A: to the documents referee ===

This is the review of an audience edition of the case [[case]]'s documents, on the git branch main: one round, by notes/briefs/audience_review.md.

The case is [[the case in one sentence: the action, against what]], in cases/[[case]]/. Its one-page summary and policy paper, the plain edition, were reviewed and accepted at milestone 2. An `audience-translator` agent re-voiced them for one audience in commit [[commit]], from the profile audiences/[[key]].toml, to the rules of its definition, .claude/agents/audience-translator.md: it may change wording, the order of sections (and in the summary of paragraphs), emphasis, boxes and the cover's icon; it may assert nothing the plain edition does not, and leave out nothing the plain edition says. Read first the definition's sections "The one rule", "What stays as it is", "What you change" and "Never"; the profile; and the case's requirements.md, which says what the case asks its documents to attend to for this reader and wins over the profile. Under review, in documents/audience/[[key]]/:
1. executive_summary_template.md and its filled executive_summary.md, from documents/executive_summary_template.md;
2. policy_paper_template.md and its filled policy_paper.md, from documents/policy_paper_template.md;
3. crosswalk.md: each block's source in the plain template, and what changed.
The plain edition is the text to check against. The paper of record behind it is documents/technical_appendix.md, with [[the results file]]; go to it only where the plain edition and the audience edition seem to differ in meaning.

4. First the mechanical checks, run from the repository root. Each prints nothing when it passes, except the counts of M4, M5 and M6.

```
C=cases/[[case]]/documents; A=$C/audience/[[key]]
num() { grep -v '^#' "$1" | sed 's/{{[^}]*}}//g; s/]([^)]*)//g' | grep -oE '[0-9][0-9.,]*[0-9]|[0-9]' | sort -u; }
img() { grep -o '!\[[^]]*\]([^)]*)' "$1" | sed 's/.*(//; s/)$//; s|.*/||' | sort; }
words() { sed 's/{{[^}]*}}//g' "$1" | grep -o -i -w -E 'half|halves|thirds?|quarters?|most|majority|nearly all|almost all|doubles?|twice|triples?|tenfold|dozens?|hundreds|thousands|millions|billions' | tr 'A-Z' 'a-z' | sort -u; }
for d in executive_summary policy_paper; do p=$C/${d}_template.md; a=$A/${d}_template.md; echo "== $d"
  echo M1; diff <(grep -o '{{[^}]*}}' $p | sort | uniq -c) <(grep -o '{{[^}]*}}' $a | sort | uniq -c)
  echo M2; comm -13 <(num $p) <(num $a); comm -13 <(words $p) <(words $a)
  echo M3; diff <(grep '^|' $p | sort) <(grep '^|' $a | sort); diff <(img $p) <(img $a)
  echo M4; for k in key-findings callout worked-example credit; do echo "$k $(grep -c "^::: *$k" $p) $(grep -c "^::: *$k" $a)"; done; grep -m1 '^::: [a-z]' $a
  echo M5; for f in $p $a; do awk 'BEGIN{RS=""} END{print NR}' $f; done
  echo M6; wc -w $C/$d.md $A/$d.md
done
```

4.1 M1, the placeholders with their counts. A line marked `>` whose placeholder the plain template lacks is a finding. A placeholder used fewer times than in the plain template is a finding unless the crosswalk shows where its sentence went; one used more often must be in the crosswalk's list.
4.2 M2, numbers typed in the audience template and not in the plain one: only those the crosswalk lists (the edition's date). Then number words ("half", "most", "double") in the audience template and not in the plain one: judge each under 5.1, since each is a number typed in words.
4.3 M3, tables line for line and image files: no output.
4.4 M4, boxes of each kind, plain then audience: the audience count is never the lower, and the summary's first box is `key-findings` (the paper has no key-findings box of its own, `author_documents.md`, message A, 5). The count of `callout` boxes rises only by boxes the crosswalk lists as a cost, a caveat or a limit; read each added callout, and a finding or a benefit set in one is a finding of yours.
4.5 M5, counted from the plain side, since a dropped paragraph has no row in the translator's crosswalk and no sample of its rows can find it. The command prints the blocks of each template, plain then audience: they differ by the added blocks the crosswalk lists. For the paper, take each section of the plain template in turn and find every one of its blocks (paragraphs, lists, boxes, tables, figures), in the plain order, in the audience section the crosswalk maps it to; that section holds those blocks and, besides, only the added boxes the crosswalk lists. For the summary, tick every block of the plain template against a row of the crosswalk. A plain block with no counterpart is a finding, and a cost, a caveat or a limit among them is the gravest kind.
4.6 M6: the word counts within 15 per cent. Then for each word in the profile's `instead_of` entries, `grep -n -i` it in the audience templates and judge each hit by the term's `rule`; a word inside a quotation, a source's title or a statute's name is no finding.

5. Then faithfulness, row by row of the crosswalk, the audience text against the plain text:
5.1 the same meaning at the same strength: every claim, cost, harm, caveat, direction of effect and degree of certainty; a hedge neither dropped, softened nor added; each quantity under the name the plain edition gives it, so that a cost to society is not called a cost to the taxpayer;
5.2 each connecting sentence (the crosswalk lists them) asserts nothing: no number, no fact about the world, the reader or the reader's institution, no citation; and there are at most three in the summary and one per section of the paper;
5.3 each quantity keeps its frame: gain or loss, total or per unit, absolute or relative, denominator, horizon, discount rate; no comparison or rescaling is added;
5.4 each swapped term names the same thing in that sentence, within the term's `rule`: no success word for an activity word ("early warning" where the plain edition says only that the system detects), no named group for a general word unless the plain edition's quantity is for that group; and no term the profile marks `apply = false` is applied;
5.5 the skim path. Read only what the profile's `reader.reads` names, in the order printed (for the summary: the title, the key findings and the boxes). From that alone a reader gets the same five answers as from the plain edition (the net benefit, its range, the cost, the main caveat, the option ranked first) and its largest cost. Any effect the edition leads with or boxes that is not the largest contributor to the result states its share of the total in the same box or paragraph, from the plain edition's placeholder. A headline number repeated in an added box carries its range and its cost each time. Where the plain edition gives no share for an effect the edition leads with, say so as a finding "in the plain edition";
5.6 no title, heading or caption claims more than its section supports, and the cover's icon shows the subject, not a verdict;
5.7 nothing from the definition's "Never" list or the profile's `voice.never`;
5.8 under each title stands the plain edition's dateline and nothing more; the edition sentence at each document's foot (the definition's "What you change", 6) is the profile's `edition_line` word for word, or the wording the task gave, and is true of this edition; and no line says what review either edition has had.
6. Then fit, briefly: does the edition do what the profile asks (its tone, its lead order, its boxes, its terms)? An edition a reader could not tell from the plain one is a finding, of low rank. Raise no wording as a matter of taste.
7. The bar is the owner's (the owner's message of 2026-11-11): "scrupulously honest in the facts and data". What counts as a finding, below, is the seat's list and tests: a plainer word, a new order, a bolder heading or a box is no finding; a changed number, a lost hedge or interval, a claim the plain edition does not make, a cost made easy to miss, or a frame changed is. Mark a stated falsehood as one.
8. A fault the plain edition already has is not the translator's: mark it "in the plain edition", for the case's author. A doubt about the profile itself, such as an entry marked `judgement` that reads as a caricature, is a finding "on the profile", for the coordinator.
9. Your definition's rules hold, with three changes: number your findings T1 onward, not D1; for the step a finding sends work back to, write "edition", "in the plain edition" or "on the profile"; there is no round 2.
10. Write your report to cases/[[case]]/review/audience_[[key]]_faithfulness.md; do not commit.
11. Your return: the verdict, the result of M1 to M6 in one line, the three gravest findings one line each, and the path.

=== MESSAGE B: to a fresh editor ===

This is the ruling on the review of an audience edition of the case [[case]]'s documents, on the git branch main, by notes/briefs/audience_review.md. The round is one: this ruling and your check of the fixes close it.

The case is [[the case in one sentence: the action, against what]], in cases/[[case]]/. An `audience-translator` agent re-voiced its accepted one-page summary and policy paper for the audience of the profile audiences/[[key]].toml in commit [[commit]], to the rules of .claude/agents/audience-translator.md: documents/audience/[[key]]/executive_summary_template.md, policy_paper_template.md, their filled documents and crosswalk.md. Read review/audience_[[key]]_faithfulness.md ([[verdict]]): a documents referee's findings T1 onward, against the plain edition, documents/executive_summary.md and documents/policy_paper.md.

1. Your test is the owner's for this layer (the owner's message of 2026-11-11): "scrupulously honest in the facts and data", while it "can and should change tone, emphasis on presentation, what parts get the most focus in callout boxes". A change of wording, order or emphasis that leaves a reader who reads only what this reader reads (the profile's `reader.reads`) with the same five answers (the net benefit, its range, the cost, the main caveat, the option ranked first) and the same sense of how sure each is, is settled. A change that would leave a reader of this edition believing something a reader of the plain edition would not is to be done. (The five answers, and the two rules of this item that say what is settled and what is to be done, are the seat's.)
2. Rule on every point by its identifier, by your definition's rule 1, with "a note in the Limits" read as "listed in the crosswalk", and the points kept in your ruling, not in review/points.toml, whose limits are the analysis's. For a fix to a sentence, give the replacement or what it must keep. Your definition's rules 2, 3, 8, 9 and 11 do not apply to this round.
3. A point marked "in the plain edition" is not the translator's: list it for the case's author, with its size. A point marked "on the profile" is not the translator's either: list it for the coordinator.
4. These are the user's: list any point that touches them, and do not rule it. The wording of the edition sentence at each document's foot and whether it names the reader's office or party; whether the plain edition travels with the edition; whether the analysis writes "Department of War"; whether an edition may quote the reader's institution's own documents.
5. On the whole, rule accept, or accept with the fixes you list. There is no second round of review.

Write your ruling to cases/[[case]]/review/audience_[[key]]_editor.md; do not commit. Your return to me, under 15 lines before the WELFARE section:
6. the ruling;
7. the fixes, one line each, or, past ten, their count and the three that matter most;
8. how many points you ruled settled, listed in the crosswalk and to be done, and how many of those are stated falsehoods;
9. the points in the plain edition and on the profile, one line each;
10. the user's items, one line each, written in the user's language.

=== MESSAGE C: to the translator, resumed ===

The review of your edition is done. The editor's ruling is cases/[[case]]/review/audience_[[key]]_editor.md, beside the referee's report, audience_[[key]]_faithfulness.md.

1. Make each fix the ruling lists, as it says, and change nothing else.
2. Bring the crosswalk up to date: the line ranges that moved, and its lists.
3. Run the documents script, the mechanical checks and the build again.
4. Commit the report, the ruling and your changes in one commit, staged by name. Its message ends with your Co-Authored-By line.
5. Your return, under 15 lines before the WELFARE section: the commit; the fixes made; any not made as listed, with why; each document's pages and the summary's body size.

=== MESSAGE D: the check of the translator's fixes (to the editor, resumed) ===

Please check the translator's fixes to the audience edition, made in commit [[commit]] (see `git show [[commit]]`), by your definition's rules 10 and 12.

1. Check that each fix your ruling listed is made as listed and that the diff changes no other sentence of the two templates.
2. Append your check to review/audience_[[key]]_editor.md, ending with a final line: accepted, or what is left.
3. Commit that file alone, with `git commit -m ... -- cases/[[case]]/review/audience_[[key]]_editor.md`. The message ends with your Co-Authored-By line.
4. Your return, under 15 lines before the WELFARE section: accepted or not, the commit, and how many of the fixes you listed were not made as listed.
