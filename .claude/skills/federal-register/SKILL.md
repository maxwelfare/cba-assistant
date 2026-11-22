---
name: federal-register
description: Finds the Federal Register documents a case needs through the Federal Register's API, stores each one in the case with its text and its sources.toml entry, cuts a document from a digitized historical issue by its citation, and, where a site refuses an automated fetch, gives the user the exact link to open and the exact file to save.
when_to_use: Whenever a case needs a US federal rule, proposed rule, notice or presidential document, its dates, its docket or its regulatory history; or a source cited as "FR" or "Federal Register" by volume and page.
---

# Federal Register: find, store, and ask the user when a site refuses

The tool is `research/federal_register.py`, run from the project's root with the project's venv. Every request goes through the project's bibliographic client, so the ledger of closed hosts, the pacing and the retries hold.

## 1 Search

1. Search the API's document index (documents published since 1994) by agency, type, dates and docket, with the case's log beside its other files:

   ```
   .venv/bin/python research/federal_register.py search --log cases/<case>/federal_register_searches.jsonl \
       --agency environmental-protection-agency --type RULE --type NOTICE \
       --from 2020-01-01 --to 2020-03-31 [--docket <docket id>] [--limit N] "drinking water"
   ```

   1.1 `--agency` takes the API's agency slug; `--type` is RULE, PRORULE, NOTICE or PRESDOCU; both repeat. The term is optional.
   1.2 It prints one JSON line per document (document number, citation, title, type, agencies, date, volume, pages, dockets, RINs, PDF and web links) and logs one row per search.
   1.3 A search that returns fewer documents than the API reported is refused and not logged: run it again later, never accept a short list.
   1.4 A reported count of 10,000 or more is the API's cap, not a count, and is refused: split the search by publication date (`--from`, `--to`) until each part reports fewer, and run every part.

## 2 Store

2. Store each document into its own folder, `cases/<case>/sources/<key>/`, the key chosen by the seat as for any source, then add the entry the command prints to the case's `sources.toml`:

   ```
   .venv/bin/python research/federal_register.py store --into cases/<case>/sources/<key> <document number>
   ```

   2.1 It writes `<document number>.pdf` (the published file from govinfo) and `text.txt`, and prints the entry: citation, licence (US government work) and the PDF's URL.
   2.2 A document with no PDF link is refused; store it by its citation (3).

## 3 The archive before 1995

3. Volume 59 (1994) and older exist only as whole digitized issues. Store a document from one by its printed citation, volume, first page and last page:

   ```
   .venv/bin/python research/federal_register.py store --into cases/<case>/sources/<key> --citation 15 3 5
   ```

   3.1 It fetches the issue through govinfo's link service into a temporary folder, cuts the pages whose first line carries the printed page numbers into `FR-<volume>-<first page>.pdf`, writes `text.txt`, and prints the entry. The whole issue is never kept in the case: one can exceed 100 MB.
   3.2 Either page not found is refused; check the citation against the issue.
   3.3 The citation comes from later documents (a rule's history section), or the literature. Failing those, search the full text of every issue on govinfo, which needs the user's api.data.gov key (`DATA_GOV_API_KEY`); without it the command refuses and names the variable:

   ```
   .venv/bin/python research/federal_register.py search --govinfo --log cases/<case>/federal_register_searches.jsonl \
       --from 1991-12-01 --to 1991-12-31 bloodborne pathogens
   ```

   A hit in volume 58 (1993) or older is the whole issue: it gives the volume and the date, and the first and last pages are read from that issue before `store --citation`. A later hit gives the document number `store` takes. A quoted phrase finds none of the older issues, so search the words unquoted.
   3.4 The entry's citation holds only the volume and pages; complete it with the agency, title and date read from the cut pages.
   3.5 Volume 60 and later is refused: use `search` and the document number.

## 4 When a site refuses

4. www.federalregister.gov blocks automated access to its website, and any host may refuse. When the command exits 2:

   4.1 Never retry, never work around it, and never fetch the website's pages (`www.federalregister.gov/documents/...`); only the API is used.
   4.2 Give the user, word for word, the link the command printed and the path it said to save the file as, and wait for the file.
   4.3 Run the same command again: it uses the saved file and fetches nothing from that host. A saved `issue.pdf` is removed once its pages are cut.
   4.4 If the API itself refused, nothing can be stored until the host reopens (24 hours, in the ledger of closed hosts); tell the user so.
   4.5 Any other refused link, such as a docket file on regulations.gov, is handled the same way: the user opens the link and saves the file as `cases/<case>/sources/<key>/<file name>`, and the seat writes its `text.txt` and entry.
