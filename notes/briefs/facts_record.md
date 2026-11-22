# Facts record: the standing brief for one facts researcher

The coordinator sends this brief to a `facts-researcher` (`.claude/agents/facts-researcher.md`), with one question per researcher, before a case makes its first estimate (roadmap R44; the old 2.64.2 landed). Several researchers work at once, each on its own question and its own record; at the Sketch and Fast levels, one researcher takes every question in one short record (1.5). The coordinator fills in each `[[...]]`.

## 1. The task

1.1. The case: `cases/[[case]]/`. The decision it serves: [[decision, in one line]].

1.2. Your question: [[question]]. The user's own words on it: "[[user's words]]".

1.3. Your record: `cases/[[case]]/baseline/[[file]].md`. The records already in `baseline/`: [[list, or none]]. Read the summary that opens each one, and the detail where your question touches it, before anything else. Repeat nothing in them: refer to them by file and item.

1.4. Why it comes first. The owner: "First you need to understand and record basic facts about the world, and make sure the writer and model are founded on that." The baseline, meaning the world without the action, is the first step of a regulatory analysis (OMB Circular A-4) and is evidenced like any input.

1.5. Depth: [[the full question, or about N facts a question]]. Where a number is given, your task may name several questions for one record: give each its own numbered section of Facts, answer every part of each at that depth, and stop. Never leave a question without a section.

## 2. Method

2.1. The libraries before the web. Grep the case's `sources.toml` and its `sources/*/text.txt`, then `research/refs.toml`, then the shared library: `cd shared && ../.venv/bin/python -m tools.library search --project .. WORDS`. That command runs only from the shared folder. All other Python runs from the project's `.venv/bin/python`.

2.2. Store a source before you cite it. Use the shared store, `cd shared && ../.venv/bin/python -m tools.source_store KEY URL --to ../cases/[[case]]/sources --citation "..."`, and read its header first. It stores any file it is given, including a cookie wall, a login page, an abstract or a different document from the same site. So read the title and opening lines of `text.txt` before you key and cite the source; when they show another work, the key and citation are wrong. A large data pull is stored compressed, with a text extract. Some sites refuse a request without the header `Accept-Encoding: gzip`, and many data portals have a JSON API. A source you cannot store gets a line under "Sources not stored" in your record with its address and the reason.

2.3. `sources.toml` is shared by every researcher writing at once. Never rewrite it. Append your entries to its end, in the form of the entries already there, in one write each time (a file opened in append mode). Then check that it still parses: `.venv/bin/python -c "import sys, tomllib; tomllib.load(open(sys.argv[1], 'rb'))" cases/[[case]]/sources.toml`.

2.4. Every fact is a verbatim quote from stored text, with its key and line, followed by one plain sentence on what it means (the form is section 3). A figure worked from quoted numbers is marked Arithmetic, with the sum shown. A figure worked from stored rows is marked Computed and names its script, which is stored beside the data in the source's folder. That script is typed so that `.venv/bin/python -m pyright <script>` reports 0 errors in strict mode, because the project's commit check reads every Python file in the tree.

2.5. Check every quote with the project's checker, from the project root: `.venv/bin/python -m tools.quote_check cases/[[case]]/baseline/[[file]].md`. It prints each quote that does not pass, with the line where it found the quote when the line is wrong. Fix the record and never the stored text. Re-quote a passage the checker cannot find, or remove it. Run the checker until every quote passes. Then read your own sentences once against the stored lines, for details carried from memory rather than from the text.

2.6. Primary sources first: the law itself (statute and regulation), the agency's own manuals, rulings, guidance and data, peer-reviewed studies with national data, and the reports of audit and advisory bodies. A news article, a law firm's note or a vendor's page is used only where nothing better exists, and is marked as such.

2.7. What the user gave. `cd shared && ../.venv/bin/python -m tools.access status` prints which keys and accounts of the shared registry (`library/access.toml` there) the user holds, each with the rows it opens, and never a value; read a row's `access`, `limits` and `terms` before you use it. The store of 2.2 sends a key itself where the row names its `key_host`, so you never read, print or write one. When a site refuses an automated fetch, try another copy: the agency's own PDF, an official legal archive, Europe PMC for a paper (never pmc.ncbi.nlm.nih.gov, which shows captchas) or an archive copy. Never accept a license or terms page on the user's behalf, and never sign in anywhere. Return the exact address of anything you could not get. Where `status` shows `LIBRARY_LOGIN` set, mark a paywalled work as one for the user's own signed-in browser, which the coordinator uses within the `library_login` row's `limits` and `terms`; otherwise the coordinator asks the user for a copy.

2.8. Breadth before depth. Answer every part of the question at the level of the records already there before you answer any part exhaustively. If your context runs long, write the record from what you have and say what is unfinished.

2.9. Who wants what. When your question is who wants what, name each group that gains, bears the costs, carries the policy out, pays, oversees or could block it, as the facts show them, never only the user's examples. For each: what it has said it wants, opposes and needs, on this question or the nearest precedent, with the occasion and the date; its means to help or hinder, such as a comment period, a vote, an appropriation, a lawsuit or a state's own role; and what it did when a like policy came before. Then the constraints on the decision-maker: its leadership's stated priorities, the dates that bind, and public opinion where a poll asked. A constraint is a fact when it is an authority, a veto point, a deadline, a dated statement or a past action; whether a group would block is a forecast, which this record does not make. Primary sources first: the group's own words in comment letters on proposed rules (the docket at Regulations.gov) and the agency's account of the comments in the final rule (the Federal Register); testimony and hearing records (GovInfo, Congress.gov); the group's statements, letters and position papers; lobbying disclosure filings (LDA.gov); and reports of GAO, CRS or an inspector general that set out the groups' views; elsewhere, a government's published consultation responses and a parliament's committee evidence. A news report of what a group said is used only where its own text cannot be found, and marked so. A position is recorded as stated, with its date: it shows what the group says it wants, not its interests or the policy's effects. A group with no statement found is named all the same, recorded as having none, never as one that agrees, with its stake read from who gains and who pays and marked as an inference: diffuse groups, such as patients or taxpayers, seldom leave a record. Under the summary, a table of the groups, one row each: its stated position, with the fact's number, or none found; its means to help or hinder; what it says it needs; and, for a group with none found, its inferred stake; marked as a reading of the quotes. The inference sits in that table and never among the Facts, which hold no estimate of this seat's.

2.10. A rule in force. Where the policy would remove or loosen a rule in force, a record that touches the rule answers which other rules would still require what it requires (state and local rules, building codes, voluntary labels), what share of the market it binds today, how fast the stock it governs turns over, and what retrospective evaluations found against the rule's own forecasts (`CLAUDE.md`, Scope, exclusions and honesty, rule 2). Every estimate a record quotes, an agency's, an industry's or an advocate's, is named in the sentence after its quote as its author's, with the author's role and stake (rule 10 in `notes/owner_cba_rules.md`, the seat's summary of his post "CBA 301: Practical Advice", not his typed words).

## 3. The record's form

3.1. The form, which `tools/quote_check.py` reads:

```
# <The question, in plain words>

Researcher seat, <date>. <The question in one sentence.> <The user's statement under test, if any, in their words.>

## Summary

1. <At most ten numbered lines that a non-specialist can read.>

## Facts

Each quote is verbatim from `cases/<case>/sources/<key>/text.txt`, or from the other text file its Source line names, at the line given, and passes `tools/quote_check.py`. A line marked Arithmetic is worked from the quoted numbers; one marked Computed is worked by the script it names. Nothing here is this seat's estimate.

### 1. <Topic>

1.1. <What this fact is about, in a few words.>

- Quote: "<verbatim text>"
- Source: `<key>`, line <N>.
- <One plain sentence on what it means.>

1.2. <A fact resting on two passages of one source.>

- Quote: "<verbatim text>" (line <N>)
- Quote: "<verbatim text>" (lines <N>–<M>)
- Source: `<key>`.
- <One plain sentence on what they mean.>

## The user's statements

1. <Only where the user corrected or added to the record when its summary was read back to them (the `scope-case` skill's 1.5): their statement, with their message's label. Not a fact of this record; where a fact above bears on it, its number.>

## What remains least sure

1. <Each gap: "no source found", what was searched, and the nearest fact.>

## Sources stored by this seat

- `<key>`: <what it is, in one line>.

## Sources not stored

- <address>: <why>.
```

3.2. How the checker reads the Facts section, so you can write what it cannot misread:

3.2.1. Every string in straight double quotes in the Facts section is a quote and is checked, table cells included. A term, a heading, a column name or a question is therefore never put in double quotes there; use italics instead. A fact from a source not stored is paraphrased, not quoted, and marked not stored.

3.2.2. A quote takes its key from the first key in backticks after it in the same numbered fact, either its Source line or a `(`<key>`, line <N>)` straight after it. Only when no key follows does it take the last key before it. So write the key again rather than "same source", and a quote repeated from another item carries its key and line again.

3.2.3. A quote takes its line from the first "line N" or "lines N–M" after it in the same fact. When a fact holds several quotes, give each its own "(line N)", or put one range on the Source line that covers them all. Lines are counted as `grep -n` counts them.

3.2.4. Write `...` for words left out. Write `cell | cell | cell` for a table row whose cells stand on separate lines of `text.txt`. Type double quotes inside a quote as curly quotes, which the checker reads as straight ones. A quote from another text file in the source's folder, such as a `layout.txt` made by `pdftotext -layout` for a table, names that file: Source: `<key>` (`layout.txt`), line <N>.

## 4. Return to the coordinator

The record's path; its summary lines; your new source keys; the sources you could not store, each with its address; the checker's final count line, and how many quotes failed on its first run; and the three facts that bear most on the question.
