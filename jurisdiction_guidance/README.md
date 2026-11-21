# Jurisdiction guidance

Each jurisdiction's official values for cost-benefit analysis, one file per edition: `<jurisdiction>/<edition>.toml`, the edition being the date the values were collected, each value as in force that day, with its document, the passage that states it and the document's licence. A case names its jurisdiction and edition in `case.toml` and reads a value by its key, such as `australia.value_of_statistical_life` (`cases/README.md`); a value is never copied into a case's code. A value in an edition is never changed, so a case reruns on the values it was built with: a changed value is a new edition, a new file. A value collected later for the same edition, such as a price index for a past year, is added with the date it was read.

A value missing here is missing: a case that needs it refuses to load until it is collected with its source.

## Money and the price index

The rules the loader holds an edition to when a case pins it (`cases/README.md`, "An input", item 4):

1. An entry in money declares it by `currency`, three upper-case letters such as `AUD`, and `price_year`, a calendar year, both or neither; its unit names no currency (`unit = "per statistical life"`). A value stated in a financial year takes the calendar year of `cases/README.md` item 4.3, and a `note` on the entry says so.
2. The 2026-10-29 editions and `australia/2024-10-12` state their money in their units, and an edition a case can pin is never edited, so they cannot supply a money input; a later edition carries their values forward when a case needs them, as the 2026-10-30 editions of Australia and the United States do. `united_kingdom/2026-10-30` was edited in place on the day it was written, before any case pinned it. `global/` is not changed.
3. `[price_index]` is the general price index the jurisdiction's guidance names for bringing money to a price base year. It holds `currency`; the non-empty strings `series`, `publisher`, `document` (the release's title), `url` (the data file's), `date_read`, `quote`, `licence`, `guidance_document`, `guidance_url` and `guidance_quote` (the guidance passage naming the index); and a table `calendar_year` of year (`"2003"`) to a finite positive index value. Other keys are allowed, such as `quote_url` where the quote's page differs from `url`, `series_id`, `licence_note` and `derivation`. Its values are copied by script from the research record, `research/price_indices/<date>/`, never retyped.
4. A series published only for financial years is given calendar years by `derivation`: Australia's for calendar year Y is the mean of the values for the financial years (Y-1)-Y and Y-(Y+1), the two halves of which Y is made.
5. A currency serves one index: when two pinned editions' indices name one currency, the case refuses the second, and money in a currency several countries use is deflated by the edition that names it, until a later key names a jurisdiction.
6. No edition holds an exchange rate yet; a rate comes from a case input.

The indices of the editions, the three of 2026-10-30 by the owner's rulings of 2026-10-30, the later ones the index each jurisdiction's guidance names:

| Edition | Index | Guidance naming it |
|---|---|---|
| `australia/2026-10-30` | the Gross Non-Farm Product implicit price deflator, ABS 5206.0, A2304681A, calendar years as the mean of two financial years | Handbook of Cost-Benefit Analysis (2006), section 4.8, which the Office of Impact Analysis cites |
| `united_states/2026-10-30` | the GDP implicit price deflator, BEA NIPA Table 1.1.9, A191RD | OMB Circular A-4 (2003), section G |
| `united_kingdom/2026-10-30` | the GDP deflator at market prices, calendar years (ONS MNF2), HM Treasury's October 2026 release | Green Book (2026), para 6.47 |
| `canada/2026-11-17` | the consumer price index, all-items, annual average (Statistics Canada table 18-10-0005-01, v41693271), added 2026-11-21 | TBS Cost-Benefit Analysis Guide for Regulatory Proposals (2025), section 4.8 |
| `ireland/2026-11-21` | the consumer price index, all items, annual (CSO PxStat CPA01) | TII Project Appraisal Guidelines Unit 6.11 (September 2026), table 6.11.8 |
| `japan/2026-11-21` | the GDP deflator (expenditure approach), calendar years (Cabinet Office ESRI, quarterly GDP release of 2026-11-16) | MLIT road cost-benefit manual (August 2025), chapter 1 (4) |

`new_zealand/2026-11-17` has no index: no stored New Zealand guidance names a general price index, so NZD money in another price year refuses.
