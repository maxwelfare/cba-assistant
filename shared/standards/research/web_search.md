DOC-CLASS: rule
# Web search patterns

A seat searches the web only after the libraries (CORE 2.2), and searches it as below. Each pattern gives its reason and its source; "not held" means the source is cited from memory and no copy is stored.

1. Start with short, broad queries, see what exists, then narrow: agents default to long, specific queries that return few results (`anthropic_2025_multiagent`, "Start wide, then narrow down").
2. Look for a scholarly work by its DOI, exact title or first author and year in a scholarly index (OpenAlex, Crossref, Europe PMC) before a general engine: the index returns the record and its open copies, where a general engine ranks optimised pages above the work (`anthropic_2025_multiagent`: early agents "consistently chose SEO-optimized content farms over authoritative but less highly-ranked sources like academic PDFs").
3. Put an exact title or passage in double quotes, and restrict a query to a domain with `site:` (an agency, a journal, a repository), since both cut results to the ones that can answer (Google Search Help, search operators; not held).
4. Take a number or a claim from its primary source (the paper, the dataset, the statute, the agency's own page), and read a secondary summary only to find that source, since a summary is one step further from the observation (`anthropic_2025_multiagent`, whose rubric scores "primary sources over lower-quality secondary sources").
5. Judge an unfamiliar site by what other sources say about it, read in other tabs, rather than by its own pages (lateral reading, Wineburg and McGrew 2019; not held).
6. After each result, note what it settled and what gap remains, and write the next query for that gap (`anthropic_2025_multiagent`: subagents "evaluate quality, identify gaps, and refine their next query").
7. Size the search to the question and stop when it is answered: a simple fact takes a few searches, and agents tend to continue "when they already had sufficient results" (`anthropic_2025_multiagent`, which budgets 3 to 10 tool calls for simple fact-finding).
8. A query names the subject in general terms, never private material (a client's documents, a project's private sources), since a query leaves the machine (`.claude/agents/source-fetcher.md` item 13).
9. A work found is stored with its text (`shared/tools/source_store.py`, through `source-fetcher` for a batch), so no seat searches for it again (CORE 2.2).
