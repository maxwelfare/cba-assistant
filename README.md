# Automated cost-benefit analysis

## 0 Start here

0.1 What this is. The maxwelfare.com CBA AI Assistant (CBA: cost-benefit analysis) runs a cost-benefit analysis from end to end in Claude Code: you describe a decision, and it returns an estimate of every effect it can find, a simulated total with its uncertainty, and documents that people can read and check. Separate AI reviewers comment on each draft as journal referees do, and an AI editor rules on their comments. It is an alpha that only its author has used, so expect faults (0.5) and report them (0.6).

0.2 What you need.

0.2.1 On the web, the recommended route: a browser, a GitHub account and a Claude plan, with nothing to install. Claude Code on the web is included in the Pro, Max, Ultra and Team plans and some Enterprise seats; this tool's runs need Max or Ultra (3.1). Usage on the web counts against the same plan limit as all your other use of Claude, so what a run costs is usage against that limit, not a bill.

0.2.2 On your own machine, the alternative, for those who want PDF documents or to work on their own computer: VS Code with the Claude Code extension, git, Python 3.13 or later, and uv, the Python package manager (3.3); and for PDFs the pinned Quarto, which `cd shared && ../.venv/bin/python tools/quarto_setup.py` installs into the copy (Typst comes inside it), the TeX Gyre fonts (`fonts-texgyre`; `fonts-noto-cjk` for Korean, Japanese or Chinese), the Poppler tools `pdfinfo`, `pdftotext` and `pdftoppm`, and MuPDF (`mutool`), with which every PDF is checked. Every document is written in Markdown and its PDF is built from that. Without Quarto, as on the web, the documents arrive as Markdown only, with the same text.

0.2.3 For the optional Google Sheet of a case's estimates, Claude's Google Sheets and Google Drive connectors, turned on in your Claude account and, on the web, enabled on the session. The sheet has not been tried from the web.

0.3 How to start. No step needs a terminal. Anthropic's quickstart shows the screens of the web steps: https://code.claude.com/docs/en/web-quickstart.

0.3.1 On GitHub, open the tool's repository, a public template, choose "Use this template", then "Create a new repository", and set yours to Private. The new repository is yours: it shares no history with the template, and every case you run stays in it.

0.3.2 Go to claude.ai/code and sign in to your Claude account. Authorize GitHub when asked, install the Claude GitHub App on your GitHub account, and give it access to your new repository: a private repository appears in Claude only if the App's repository access includes it.

0.3.3 Before the first run, in the cloud environment's settings, set Network access to Full, which lets the session reach any site. The default network access level does not reach the literature indexes the tool searches or the journal and government sites it fetches sources from. If you skip this step, the session stops at the first blocked source and offers a list of allowed sites for that one case (4.3.2).

0.3.4 Pick your repository in the selector below the input box and ask Claude to set the tool up. uv, git and Python come installed there. It builds the Python environment from the lock file and runs the tests.

0.3.5 Say what you want analyzed and what decision it informs, for example "Is it worth funding a program that ...?" Claude holds a requirements conversation, asks how thorough the work should be (0.4), and reads everything back for you to confirm before the run starts.

0.3.6 Where your work is. Each task works on its own branch and pushes it to your repository. You read what it wrote in the diff view at claude.ai/code and on GitHub, where Markdown documents display formatted. The "Create PR" button opens a pull request, and merging it puts the case on your main branch. Closing the browser tab does not stop a session, and you can continue it later from claude.ai/code or from the Code tab of Claude's mobile app.

0.3.7 The alternative, on your own machine (0.2.2). After 0.3.1, in VS Code, open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on a Mac), choose "Git: Clone", then "Clone from GitHub", sign in to GitHub when asked, and pick your new repository. Open the folder, and say yes when VS Code asks whether you trust it (4.2). Open Claude Code from its icon, sign in to your Claude account, ask it to set the tool up, and go on from 0.3.5.

0.4 The four levels: what you get, and what it has cost on the record, in dollars at Anthropic's list prices (0.2.1).

0.4.1 Sketch: a range for each good and bad effect, shown in the chat, unreviewed and with no total. Its cost is not measured.

0.4.2 Fast estimate: adds a Monte Carlo total with a 90% interval, a short technical note, a one-page summary, three AI referees' comments and an editor's letter. Two simulated clients each finished one, in a little over an hour each of conversation and run time, for $24 and $25. The tool's own card quotes an earlier run, about $32.

0.4.3 Normal: adds a small model for each effect the review flags, a revised technical appendix and a policy paper, whose PDF is also built with the one-page summary in front. It is the level with the known faults of 0.5. On the record, a large analysis at this level took more than a day of attended sessions and over $350 in its last session alone; a small one reached its accepted appendix for about $54 (5.1.1).

0.4.4 Full: adds a systematic review of the inputs you choose. That review is in its first trial, and the tool does not yet offer Full whole.

0.4.5 Start with a fast estimate. The tool's card recommends Normal, its default; for a first run choose the fast estimate anyway. You can go on to Normal from there, and the work carries over.

0.5 Where it is rough.

0.5.1 A revision tends to rerun the whole review, where only what changed needs it.

0.5.2 A ruling you give on presentation, such as units, rounding or spelling, may not reach every document: check each one.

0.5.3 The documents of the Normal level are slow to write, and their PDF layout may need fixing.

0.5.4 Long tables restate inputs row by row.

0.5.5 The requirements conversation can skip a topic or understate a cost.

0.5.6 Two steps are new in this update and have been tried once only: the record of the facts of the situation today, each a quote checked against its stored source (`notes/briefs/facts_record.md`), and, where you bring a goal and no designed policy, research before the options are designed with you (`.claude/skills/scope-case/SKILL.md`, section 1).

0.5.7 Some instructions still point at tools this copy does not carry (6.3). When an agent stops over one, tell it to go on without it.

0.5.8 A stored copy of a source is a convenience. This copy leaves out those it may not redistribute, and the tool's agents fetch a missing one from its address when they need it.

0.5.9 On the web, documents arrive as Markdown, not PDF, since Quarto is not installed there; a case's versions, which the tool keeps as git tags, are not tagged, since a web session cannot push a tag: the session tells you the version's number and its commit, and the tag is still to be made from a machine that can push one; and after a long pause the helpers that were running in the background are gone, so tell Claude to carry on from the files (4.3.4).

0.6 Feedback. Open an issue on the template repository with its "Alpha feedback" form, or write to the author. Put nothing confidential in an issue.

0.7 Updates. When a newer version of the tool is published, a session tells you so and, on your yes, upgrades your copy in one commit that keeps your `cases/` folder, `user.md` and `organizations/`.

## 1 What it does

1.1 You describe a decision: a policy, program, grant, regulation, investment or research project, and what it would be compared with. Claude holds a requirements conversation with you. It first reads what you have already given it, then turns your question into a decision problem a model can answer: the options and the base case, who gains and who pays, which effects count, how the model is built and which inputs it needs. Last, one question at a time, it covers what else could change the result or what you receive, such as how thorough the work should be (one of four levels: a sketch, a fast estimate, Normal and Full; 1.2 and 1.3), whether a national guideline binds it, what must not be priced, how far to put effects into money and what is confidential. It reads everything back to you as a numbered list to confirm or correct, and records what you confirm as the case's requirements (`requirements.md`), against which the design and its reviews are checked. It writes the case's index (`CASE.md`) and design (`design.md`) beside them, in a folder of its own under `cases/`.

1.2 The work is broad but shallow (`notes/fast_estimate.md`). Three helpers, each blind to the others, list every good and bad effect of the policy, each from an angle of its own, and each effect gets a rough estimate by hand: a product of a few factors, each with a low, a middle and a high and its source, the arithmetic written out. A sketch shows you each effect's range in the conversation, unreviewed and with no total. From a fast estimate up, one author agent then writes a fast draft straight through, with no code: each source stored in the case's folder; the estimates totaled by a shared tool as a Monte Carlo simulation, so that the total is a distribution with a 90 percent interval, never a single number; a short technical note that works each effect out as an example; and a one-page summary. Three reviewer agents then comment on the draft (an economics referee, an audit referee who traces every factor to its source and reruns the total, and a documents reviewer), and an editor turns their comments into one decision letter, which names the few effects worth a model. A fast estimate stops there.

1.3 At Normal, the default, the same author then upgrades the draft, reviewed as a journal reviews a paper. It builds a small model in plain Python, about six inputs on one spreadsheet tab, for each effect the letter names, each input's quote checked against its stored source by machine; the author revises and answers every point of the letter; the referees review the revision; a separate editor rules on each point and on the whole. Full adds a systematic review of the inputs you pick, and is not yet offered whole (0.4.4). A point that is yours to decide, such as a value judgment or what the analysis is for, is never settled by the agents: the editor lists it, and it comes back to you as a question with a recommendation.

1.4 Every agent works to the rules for a cost-benefit analysis set out in `CLAUDE.md`, drawn from Richard Bruns's posts "CBA 301: Practical Advice" (2025) and "Welfare Estimation 201" (2022) on the EA Forum. The literature for and against each rule is in `research/cba_301_practical_advice.md` and `research/welfare_estimation_201.md`, a good place to start if the field is new to you.

## 2 What a case delivers

2.1 What a finished case holds, in its folder under `cases/`. This copy holds no case: `cases/` has its README alone, which says how a case's folder is laid out.

2.1.1 `inputs.toml` and `sources.toml`: every input with its distribution, quote and source; every source with its citation and license, and its stored text and original document in `sources/`.

2.1.2 `effects/`, `estimates/` and `estimates.toml`: the lists of effects and the estimates by hand, totaled into `results/`; and, only where a small model was built (Normal and Full), `model.py` and `run.py`, the model and its run from a fixed random seed, writing its results to `results/`.

2.1.3 `documents/`, in Markdown: a technical appendix written as an academic paper, with every formula and citation; then, as the run's second milestone, a policy paper of about 20 pages for educated non-specialists and a one-page summary in plain language. That second milestone's standing instructions for its agents are `notes/briefs/author_documents.md`.

2.1.4 `review/`: every reviewer's report, decision letter, response letter and ruling.

2.2 Typeset PDF documents are built: `tools/typeset.py` turns a case's Markdown documents into PDFs, and the `pdf-layout` agent reviews their layout. Written but not yet used on any case: a peer review package for each human peer reviewer, made by the author at the end of the run where the user asks for one, in `review/packets/` (`notes/briefs/reviewer_packet.md`); and an expert survey for the inputs that matter most, whose form a script writes (`tools/elicitation_form.py`), though its replies are not yet taken back into the model. Not built: packets for analysts who audit the automated steps, and a systematic literature review of the most important inputs (in progress).

## 3 What you need, in detail

3.1 The plan (0.2.1): a run's many helpers use more than a Pro plan allows (the owner, 2026-11-10: "I will tell people they need max or ultra"). Every run recorded in section 5 used Claude Opus 5.5 for its agents, with Claude Sonnet 5.5 for some helpers. No other model provider is needed. A power user running a clone (4.5) may choose others: `/model` picks the session's model and each agent definition's `model:` line its helper's, and Claude Code reaches Claude through Amazon Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), Google Vertex AI (`CLAUDE_CODE_USE_VERTEX=1`) or an LLM gateway named by `ANTHROPIC_BASE_URL` (Claude Code's documentation, "Third-party integrations"). The tool is tested only with the Claude models above.

3.2 The Python version (0.2.2) is the one `pyproject.toml` requires.

3.3 uv wrote the lock file, `uv.lock`. It builds the project's own environment, `.venv`, at the exact versions the lock file pins: NumPy and SciPy, and for development pytest, pyright, the SciPy type stubs and uv itself. `pyproject.toml` pins uv 0.13.6 among those development tools; the lock file does not record which version of uv wrote it.

3.4 On the web, the recommended route, you install none of this: uv, git and Python come installed in the cloud environment, and the session builds `.venv` there as it does on your own machine (4.3).

3.5 Optional: keys for the literature search and for public datasets, asked for when a case needs one. You make the account and agree to its terms, which only you can do; the session does the rest, and never asks you to edit a shell profile or use a terminal (the owner, 2026-11-08, when a key pasted in a terminal came out wrong: "Give me a link to a file I can edit"). Each key has one name, given in its source's row of the registry (`shared/library/access.toml`), and is read from the environment variable of that name or else from a file of yours outside the repository (`~/.local/share/research-keys/NAME`; for the OpenAlex key of the literature search tool, `research/bibliography.py`, `~/.local/share/openalex/api_key`): on your own machine the session makes that file and gives you a link to it, to paste the key into; on the web you paste `NAME=key` into your cloud environment's Environment variables (the environment selector under the message box, then Edit).

## 4 How to start, in detail

4.1 On the web, the recommended route, the steps are 0.3.1 to 0.3.6, and 4.3 gives their detail. On your own machine, the steps are 0.3.1 and 0.3.7. VS Code's Extensions view installs the Claude Code extension. A folder you downloaded opens with File, then Open Folder, in place of the clone. In the set-up the session builds the project's environment, `.venv`, with uv (3.3).

4.2 On your own machine, open the folder in VS Code. It asks whether you trust the authors of the files in it: say yes, since Claude Code does not run in the Restricted Mode VS Code otherwise opens the folder in (if a bar at the top says "Restricted Mode", click its Manage, then Trust). In a new install of VS Code a panel first asks you to sign in to GitHub Copilot: continue without signing in, or close the panel, since this tool runs on Claude Code, not Copilot. Then open Claude Code from its icon and sign in to your Claude account when it asks. To see only Claude's messages, with its helpers' steps folded into rows you can open, turn on Focus view: press Ctrl+Alt+F (Ctrl+Option+F on a Mac), or type / in Claude's box and choose Focus view. When you ask about a new analysis, or what the repository does, Claude starts the requirements conversation, whose instructions are `.claude/skills/scope-case/SKILL.md`. A new copy with no case yet greets you with one welcome line when Claude Code starts; otherwise Claude waits for you to speak first. When you have confirmed the requirements and the design, the design goes to the case's author, and the run continues without you until the draft and its reviews are ready.

4.3 On the web, the recommended route, with nothing to install: the steps of 0.3.1 to 0.3.6.

4.3.1 Start a session on the repository, not a thread inside a claude.ai/code project: the documentation promises that the repository's helper definitions load in a session "outside a project's threads", and those helpers are how the work gets its independent review.

4.3.2 Network access. The default network access level reaches the Python package index but not api.openalex.org, api.crossref.org or eutils.ncbi.nlm.nih.gov, which the literature tools call, nor the journal and government sites that sources are fetched from. Full lets the session reach any site; or add those domains to your environment's allowed list. With the default network access every source's site is blocked, so only web-search summaries come through and nothing can be stored or quoted. The session then shows "This environment's network access blocked a host Claude needs" with an "Edit cloud environment" button, and Claude offers to create a new environment for the repository with a list of allowed sites for that case. Such a list works for that case and is asked for again at the next, since each case cites different sites. If you have material that you must keep in, the list is the safer choice, at the price of approving it for each case.

4.3.3 What it costs. Your plan pays, the machine is free, and usage counts against the same plan limit as all your other use of Claude (0.2.1). A Console or API-key account cannot use this route.

4.3.4 Limits on the web. Quarto is not installed, so documents arrive as Markdown, not PDF; the route on your own machine, with Quarto installed (0.2.2), makes PDFs. A session cannot push a git tag, so a case's versions, which the tool keeps as tags, are not tagged from the web: the session tells you the version's number and its commit, and the tag is still to be made from a machine that can push one. An idle session's machine pauses after a few minutes and can be reclaimed: the conversation is restored but helpers running in the background are not, so after a long pause tell Claude to carry on from the files. The optional Google Sheet needs the Google Sheets and Google Drive connectors enabled on the session; the documentation says that connectors enabled on a session work, and this has not been tried here. An API key, where you use one, goes in the cloud environment's environment variables (3.5).

4.3.5 What has been tried. On 2026-11-12 a web session on a copy of this tool loaded the instructions, all the agent definitions and both skills, ran one helper end to end, installed the environment, ran the tests and pushed a branch. The author has started a case on the web. No case has yet been run to its documents there, so report what breaks (0.6).

4.4 To know what the agents are told, read `CLAUDE.md`; how a case's folder is laid out is `cases/README.md`; the tools a case's model may use are listed in `cost_benefit_engine/README.md`.

4.5 For power users, from a terminal: the same set-up by hand, from the folder you clone into.

```
git clone <the repository's address> automated-cost-benefit-analysis
cd automated-cost-benefit-analysis
uv sync --frozen
.venv/bin/python -m pytest
```

## 5 What a run costs

5.1 The record by level is 0.4. Two earlier runs are recorded here, both before 2026-11-10, when a case's first draft still built its model in Python. Neither figure includes the conversation that starts a case or the Claude Code session that dispatched the agents. Dollars are at Anthropic's API list prices (0.2.1). How they were made: each agent's output, read from its transcript of the run, priced at about $57 a million output tokens, the all-in rate for Opus, cached reading included, that the author's token ledger, which this copy does not carry, shows over all its sessions (the method of `.claude/skills/scope-case/presets.md` 10.1); times from the transcripts' timestamps. Both are estimates to two figures.

5.1.1 Normal, fast draft then upgrade. The fast draft was written in 40 minutes, for about $15. The upgraded technical appendix was accepted by its editor 2 hours 31 minutes after the start, for about $54 in all. The whole Claude Code session that ran it, including other work on the tool beside it, cost $75.09 by the author's token ledger, at the prices it read then; it now reads the shared price table, `shared/tools/token_prices.json`.

5.1.2 Normal under the reviewed process, with no fast draft first, through both milestones: about $49 and 2 hours 25 minutes.

5.2 Both were small cases, and two runs are too few to predict a third. The later record of 0.4 runs from tens of dollars for a fast estimate to hundreds for a large case at Normal, before any systematic literature review.

## 6 Status, and what is not yet in place for a new user

6.1 Status: alpha. Built and in use by its author: the case process of section 1; the toolbox of model components, `cost_benefit_engine/`; dated guidance values for Australia, the United Kingdom, the United States and a global transfer method, each with its source, `jurisdiction_guidance/`; and tools to search OpenAlex, Crossref and PubMed and to record screening decisions, `research/`.

6.2 Your cases live inside the tool's own folder, `cases/`, in the same repository as the tool. A separate workspace, so that your cases sit in a private repository of their own and updating the tool never touches them, is designed but not built. Until it is, keep any copy that holds a case you cannot share private.

6.3 The author works from a shared set of methods and tools that serves several of his projects. This copy carries the part of that set the tool reads: the core instructions, inside `CLAUDE.md`; in `shared/`, the modeling red flags, the writing rules, the methods for weighing checks, for peer review, for licensing and for the welfare check, the output style, the list of current AI sources, the shared library's index and its search, the source store with its fetch tools, and the token price table; and in `.claude/agents/`, the referee and quick-reader agent definitions. It does not carry the rest: the author's memories, decisions record and roadmap, the build workflow, the session close and the other shared tools. Some instructions still name one of those, and an agent that looks for it will not find it (0.5.7). Where an instruction names a folder of the author's machine, the copy gives the path in this repository.

6.4 The requirements conversation of 1.1 is written and has been tried by three simulated clients and in the owner's own pass. After its first two turns it sends helpers to list every good and bad effect of the policy, shows you their list, lets you put your own rough number on any effect, and then shows rough estimates by other helpers while the conversation goes on. It asks how thorough the work should be as a choice of the four levels of 0.4. Add-ons, such as a spreadsheet or packets for human reviewers, are offered once a result is in. It keeps what you confirm about yourself and your organizations, in `user.md` and `organizations/`, for your later analyses, and these sit in the tool's own repository beside your cases until the workspace of 6.2 is built. A document you supply is stored with the case and a helper writes a table of each requirement it states, against where the analysis meets it. A table in the technical appendix of every value judgment and method choice with its source is built into the author's brief and has not yet run on a case.

## 7 License

Copyright Max Welfare Inc. The code is under the MIT License, the text under Creative Commons Attribution 4.0, and the data the project made and its results are dedicated to the public domain under CC0 1.0; third-party material, such as stored copies of sources, keeps its owners' terms. `REUSE.toml` gives the license of every file and `LICENSES/` holds the texts; `LICENSE.md` says it in full. To cite the work, use `CITATION.cff`.
