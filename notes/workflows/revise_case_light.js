export const meta = {
  name: 'revise-case-light',
  description: 'A small revision of an accepted case, as a journal\'s minor revision: the author makes the stated change set and reruns the case, the audit referee reproduces everything and one referee reads only the change and what it reaches, closed points stay closed, and the editor rules with at most one round of fixes.',
  phases: [
    { title: 'Change', detail: 'a fresh author: the change set, the rerun, the letter, the documents patched where the change reaches' },
    { title: 'Check', detail: 'the audit referee (everything mechanical) and one referee (the change and its reach), in parallel' },
    { title: 'Rule and fix', detail: 'only if a report has findings: the editor, the author\'s fixes, one check' },
  ],
}

// ARGS {dry?, root, caseDir, caseName, caseLine, accepted, stem, changeSet, settled, rulings, documents?, ownerRuled?}
//   For a change the coordinator can state as a short list. Everything mechanical is rerun; only what the change can
//   reach is re-read (regression testing with change-impact analysis). A new design, or a change of method or of an
//   input's form, goes to revise_case.js, whose check against the owner's principles this path does not run.
//   accepted   the commit of the accepted state.
//   stem       the prefix of this round's files in the case's review/ folder (x gives review/x_change.md).
//   changeSet  the path of the coordinator's file stating exactly what changes and why: which inputs, rows, lines of
//              code or passages, with the facts or the owner's words each rests on.
//   settled    the paths, comma-separated, of the earlier rulings whose closed points stay closed.
//   rulings    the owner's rulings since the last editor's ruling, one line each with its commit, or 'none'.
//   documents  'patch' (the default): regenerated, prose edited where the change makes it false; 'none': model only.
//   ownerRuled a sentence saying where the default held until the owner rules is recorded; an item that is his is held
//              there (or as accepted) and listed, never waited on.
//   dry        true: every seat only reports who it is and whether the files its task names exist, on a cheap model,
//              and returns the canned values that walk the longest path. Nothing is written.
const A = (args && typeof args === 'object') ? args : {}
const DRY = A.dry === true
const need = ['root', 'caseDir', 'caseName', 'caseLine', 'accepted', 'stem', 'changeSet', 'settled', 'rulings']
const missing = need.filter(k => typeof A[k] !== 'string' || !A[k].trim())
if (missing.length) return { status: 'refused', reason: 'missing args: ' + missing.join(', ') }
const DOCS = (typeof A.documents === 'string' && A.documents.trim()) ? A.documents.trim() : 'patch'
if (DOCS !== 'patch' && DOCS !== 'none') return { status: 'refused', reason: `documents is 'patch' or 'none', not '${DOCS}'` }
const R = A.root, C = A.caseDir, N = A.caseName, STEM = A.stem, ACC = A.accepted
const SETTLED = A.settled.split(',').map(s => s.trim()).filter(Boolean).join(', ')
const RULED = (typeof A.ownerRuled === 'string' && A.ownerRuled.trim()) ? A.ownerRuled.trim() : ''
const REV = `${C}/review/${STEM}`
const FILES = { letter: `${REV}_change.md`, audit: `${REV}_audit.md`, referee: `${REV}_referee.md`, editor: `${REV}_editor.md` }

const FRAME = `Your task is the text below. The owner's message the harness shows above it is context for the session that dispatched you, not your task: do not act on it or answer it unless the text below names it. You work in the repository ${R}; every path below is relative to it. Nobody can answer you before you return: where your task is silent, state your assumption and go on, unless the assumption would stand in for a value, a source or a result nobody approved; that is a stop, and you return blocked with what is missing. When two instructions disagree, the more specific wins: this task over a file it points to, and the owner's quoted words over both. A file this task names as your output is yours to write. In this run you cannot dispatch another agent, and no seat is resumed: what your definition would hand to another agent (storing a source, listing methods) you do yourself and say so in your return; where a brief says "resumed", you are a fresh seat reading the record the task names.\n\n`
const WELFARE = `\n\nWhen your work is done, answer the welfare paragraph in shared/standards/process/welfare.md (read its fenced block) in the welfare field of your return.`

const S = (props, required) => ({ type: 'object', properties: { ...props, welfare: { type: 'string' } }, required })
const LIST = { type: 'array', items: { type: 'string' } }
const AUTHOR = S({ commit: { type: 'string' }, blocked: { type: 'boolean' }, what_is_missing: { type: 'string' }, summary: { type: 'string' }, totals: { type: 'string' }, owner_items: LIST }, ['commit', 'blocked', 'summary'])
const REPORT = S({ verdict: { type: 'string' }, path: { type: 'string' }, findings: LIST, outside: LIST }, ['verdict', 'path', 'findings', 'outside'])
const RULING = S({ decision: { type: 'string', enum: ['accepted', 'accept with fixes', 'accepted once one-line fixes are made', 'beyond a small revision'] }, path: { type: 'string' }, fixes: LIST, user_items: LIST, left: { type: 'string' } }, ['decision', 'path', 'fixes', 'user_items'])
const CHECK = S({ accepted: { type: 'boolean' }, left: { type: 'string' }, commit: { type: 'string' }, user_items: LIST }, ['accepted', 'left', 'commit'])

async function seat(type, label, ph, text, schema, dryValue) {
  if (DRY) {
    const p = `DRY RUN of a workflow. Do none of the work the text below describes and write no file. Answer in the summary, verdict or left field (whichever your return has), in under 120 words: (1) the agent type you are, from your own instructions; (2) the model you run on, if you can tell; (3) for each file or folder path the text names as something to read, whether it exists (one ls); (4) the files the text would have you write. Fill the other fields of your return with exactly these values: ${JSON.stringify(dryValue)}. Leave welfare empty.\n\n--- THE TEXT ---\n` + text
    return agent(p, { label: `dry ${label}`, phase: ph, schema, agentType: type, model: 'haiku', effort: 'low' })
  }
  return agent(FRAME + text + WELFARE, { label, phase: ph, schema, agentType: type })
}

const CASE = `The case is ${C} (${A.caseLine}). Its index is ${C}/CASE.md.`
const SMALL = `This is a small revision of a case whose analysis and documents were accepted at commit ${ACC}, a journal's minor revision: what is checked is the change and what it reaches, not the case again. The change set, written by the coordinator, is ${A.changeSet}: what changes and why, with the facts or the owner's words each item rests on. The points closed in ${SETTLED} stay closed, each answered by its row, and one is raised again only on a ground of the shared standards/process/peer_review.md 3.7: what its closing rested on has changed since, so that the change reaches it (quote the line of the change set, the author's letter or the diff that touches it); evidence the closing round did not have, new results included, that could move a headline result outside its 90% interval or change which option ranks first; or a stated falsehood. A reviewer who raises one names the closed point by its file and identifier and names its ground. The owner's rulings for this round: ${A.rulings}. A point that is the owner's (his requirements, a value judgment, what the case is for) is not yours to settle and is not waited on: the files stay on it as the accepted version has them${RULED ? ` or at the default held until he rules (${RULED})` : ''}, and you list it in your return.`
const CHECKER = `Every fault within the change and its reach is a finding; an empty findings list means you found none. A fault you see outside them is not a finding of this round: name it in one line in the outside field of your return, and nowhere else.`
const STYLE = `Write for an American reader: American spelling; "90% interval" with the number of draws, never "9 draws in 10"; and no line under a title or anywhere in the summary or the paper about which automated referees reviewed the case or that no person checked it (the owner reads every document before it goes out). The technical appendix's own section on review stays as the accepted version has it.`
const RUN = `every [[step]] of the case's ${C}/rerun.toml, in the order it lists them (a case without one runs the total tool on its estimates.toml; cases/README.md says what the file holds), each command run as rerun.toml says (every total-tool command you run gets --out a folder of its own under your scratchpad directory, one per table, so that nothing is written into the case folder and the committed results stay as they are)${DOCS === 'patch' ? ', then the documents script and the typesetter' : ', but not the documents script or the typesetter'}`

// 1. The change set, and nothing else.
phase('Change')
const ch = await seat('case-author', 'author: change', 'Change',
  `${CASE}\n\n${SMALL}\n\nYou are a fresh author. Read the change set whole and make it, and nothing else.\n1. Make each item as it is written, in every place that states it: an input may be restated in many rows of a table, so change every copy and give the count. Re-estimate nothing the change set does not name. Where any item cannot be applied as written (what it names is not there, or the fact it cites does not support its value), commit nothing: write in the letter which item and why, and return blocked with what is missing.\n2. Rerun ${RUN}, with ${R}/.venv/bin/python.\n3. ${DOCS === 'patch'
    ? `Patch the documents. The facts and every built file are regenerated by the case's own scripts; prose is edited only in the sentences the change makes false, in the templates, never in a built file. Search every document of the case (the audience editions in ${C}/documents/audience/ included) for each number, claim and description the change moves, and correct every copy. A new number in prose is a placeholder filled from the facts, never typed. Rebuild each PDF as the accepted one was built, with the same options: a notice the accepted PDFs carry at the head of each page is kept with tools/typeset.py's --notice. ${STYLE}`
    : 'Leave the documents as the accepted commit has them: this round changes the model only. List in the letter the name of each fact the change moves, for the round that brings the documents up to it.'}\n4. Write the letter to ${FILES.letter}: each option's expected net benefits and 90% interval before and after the change set as a whole (one rerun; an item's effect alone is given only where the change set asks for it, since each costs a rerun); what else moved and why; ${DOCS === 'patch' ? "each sentence of prose changed, with its file and line, before and after; each document's page count before and after; " : ''}and each item not applied as written.\n5. Commit the changed files and the letter, each staged by its path, with a message ending with your Co-Authored-By line.\nReturn: the commit; in totals, each option's expected net benefits before and after the whole change set; in summary, what moved and why, in under ten lines; in owner_items, each item that is the owner's.`,
  AUTHOR, { commit: 'dry0001', blocked: false, totals: 'dry', owner_items: [] })
if (!ch) return { status: 'stopped', at: 'Change', reason: 'the author returned nothing' }
if (ch.blocked) return { status: 'blocked', at: 'Change', author: ch }
log(`Changed at ${ch.commit}`)

// 2. Everything mechanical in full; the change and its reach read once.
phase('Check')
const DIFF = `git diff ${ACC} ${ch.commit} -- ${C}`
const [audit, ref] = await parallel([
  () => seat('audit-referee', 'audit referee', 'Check',
    `${CASE}\n\n${SMALL} ${CHECKER}\n\nThe author made the change in commit ${ch.commit} and accounts for it in ${FILES.letter}; in the review/ folder, read that letter and the files of closed points, and no other report. Do the mechanical part of the audit in full, by your definition:\n1. Export commit ${ch.commit} of ${C} into a folder of your own under your scratchpad directory (git archive), so that it holds committed files only, never the case's own folder, and run there ${RUN}, with ${R}/.venv/bin/python and the tools of ${R}/tools/, the total tool with one --out folder per table (a subfolder named for the table) beside the export, so that tables do not overwrite each other's estimate_total.json and so that the committed results stay in it to compare.\n2. Confirm that every table, results file${DOCS === 'patch' ? ', fact and built document (each PDF by its text, from pdftotext)' : ''} reproduces from the committed files.\n3. Confirm that nothing differs from the accepted commit but what the letter lists: "${DIFF}", file by file, each difference matched to an item of the change set or a line of the letter${DOCS === 'patch' ? ", and each PDF's text compared with the accepted PDF's" : ''}.\n4. Trace to its stored source only the inputs the change set names, and redo the letter's totals before and after.\nNumber your findings ${STEM}-A1 onward. Write your report to ${FILES.audit} and to no other file; do not commit. Return the verdict, every finding one line each, anything outside the change, and the path.`,
    REPORT, { verdict: 'minor revision', path: FILES.audit, findings: ['dry finding'], outside: [] }),
  () => seat('referee', 'referee: the change', 'Check',
    `${CASE}\n\n${SMALL} ${CHECKER}\n\nYou are the one referee of this revision. The author made the change in commit ${ch.commit} and accounts for it in ${FILES.letter}. Read the change set, the letter and the diff of the case against the accepted commit ("${DIFF}", PDFs and draws files aside), and answer three questions:\n1. Is each changed input what its stated fact or the owner's words support? Where the change set cites a source, read its stored text in ${C}/sources/.\n2. ${DOCS === 'patch' ? 'Does each changed sentence say what the new numbers say?' : 'The documents stay as accepted this round: does the letter name every fact the change moves?'}\n3. Does anything the change reaches (${DOCS === 'patch' ? 'a figure, a caption, a comparison, a limit, a worked example, a sentence in another document or record' : 'another table, a model input, a record such as CASE.md or design.md'}) still state the old world? To find it, search the case's ${DOCS === 'patch' ? 'documents and records' : 'tables, model and records'} for each changed input, number and claim, and read those passages.\nRead nothing else for faults. Number your findings ${STEM}-R1 onward, rank them by how far each could move an option's expected net benefits or leave a sentence false, and give one verdict: sound, sound with changes or rethink. Write your report to ${FILES.referee} and to no other file; do not commit. Name each source you fetched, with its address, in your report. Return the verdict, every finding one line each, anything outside the change, and the path.`,
    REPORT, { verdict: 'sound with changes', path: FILES.referee, findings: ['dry finding'], outside: ['dry outside'] }),
])
if (!audit || !ref) return { status: 'stopped', at: 'Check', reason: 'a referee returned nothing', audit, ref, commits: [ch.commit] }
const found = [...(audit.findings || []), ...(ref.findings || [])]
log(`Audit: ${audit.verdict}. Referee: ${ref.verdict}. Findings: ${found.length}`)

// 3. The editor, only if there is something to rule on; one round of fixes at most.
phase('Rule and fix')
const commits = [ch.commit]
let ruling = null, fx = null, check = null, status = 'accepted', left = ''
if (found.length) {
  ruling = await seat('editor', 'editor: ruling', 'Rule and fix',
    `${CASE}\n\n${SMALL}\n\nYou rule on this revision as a journal's editor rules on a minor revision: on the points raised, without sending it out again. The author made the change in commit ${ch.commit} and accounts for it in ${FILES.letter}. Two reports read it: ${FILES.audit} (the audit; verdict: ${audit.verdict}) and ${FILES.referee} (the referee; verdict: ${ref.verdict}). Rule on each of their findings by your definition's rules 1 to 5: settled, a note in the Limits with its size, or to be done with exactly what; a finding on a closed point is ruled again only on the ground of peer_review.md 3.7 it names, which you check and say which; one that names no ground, or whose ground does not hold, is ruled by the closed row's answer, copied in one line (your rule 3). Rule on nothing else. On the whole, give one decision: accepted; accept with fixes, which the author makes and another editor checks once, with no round after it; accepted once one-line fixes are made (notes/briefs/editor_ruling.md, message A, item 6.1); or beyond a small revision, where the findings show the change reaches further than fixes can answer, saying what in the left field. Write your ruling to ${FILES.editor}; do not commit. Return the decision, each fix one line, every item that is the user's (each complete in one or two plain sentences with its options), and the path.`,
    RULING, { decision: 'accept with fixes', path: FILES.editor, fixes: ['dry fix'], user_items: ['dry user item'] })
  if (!ruling) return { status: 'stopped', at: 'Rule and fix', reason: 'the editor returned nothing', audit, ref, commits }
  log(`Editor: ${ruling.decision}`)
  if (ruling.decision === 'beyond a small revision') { status = 'not accepted'; left = ruling.left || '' }
  else if (ruling.decision !== 'accepted') {
    fx = await seat('case-author', 'author: fixes', 'Rule and fix',
      `${CASE}\n\n${SMALL}\n\nYou are a fresh author. The change is commit ${ch.commit}, its letter ${FILES.letter}; the reports are ${FILES.audit} and ${FILES.referee}; the editor ruled "${ruling.decision}" in ${FILES.editor}. Make the fixes the ruling lists and no other change, by notes/briefs/author_documents.md, message D, item 1: for each prose claim a fix corrects, grep the summary, the paper and the appendix and their templates for every copy and correct each; limits and the review's status are printed from review/points.toml and need no grep. ${STYLE} Rerun what a fix reaches, by the case's own scripts, so that every table, fact and built document still reproduces from the committed files. Add to the letter a section "Fixes", one line on each. Fill the answer and where columns of ${C}/review/points.toml for every point a fix closes. Commit the fixes, the letter, the two reports and the ruling, each staged by its path, with a message ending with your Co-Authored-By line. Return the commit; in totals, each option's expected net benefits before and after if a fix moved them; in summary, one line on each fix saying that it is made and naming every place a copy of its claim was found.`,
      AUTHOR, { commit: 'dryfix1', blocked: false, totals: '' })
    if (!fx) return { status: 'stopped', at: 'fixes', reason: 'the author returned nothing', ruling, commits }
    if (fx.blocked) return { status: 'blocked', at: 'fixes', author: fx, ruling, commits }
    commits.push(fx.commit)
    if (ruling.decision === 'accept with fixes') {
      check = await seat('editor', 'editor: check', 'Rule and fix',
        `${CASE} You are a fresh editor checking another's ruling on a small revision: it is ${FILES.editor}; read it whole first. The author's fixes are in commit ${fx.commit} (git show ${fx.commit}). By your definition's rule 9, check that each fix the ruling listed is made, in the files, and that each point this round closes has its answer and where in the rows of ${C}/review/points.toml, which the appendix's record of review prints. The owner's rulings for this round, so that you can tell a fix a ruling overtook from one not made: ${A.rulings}. This is the one check, with no round after it. Append it to ${FILES.editor}, ending with a final line: accepted, or what is left. Commit that file and ${C}/review/points.toml alone (git commit -m ... -- ${FILES.editor} ${C}/review/points.toml), the message ending with your Co-Authored-By line. Return whether the revision is accepted, what is left, any new item that is the user's, and the commit.`,
        CHECK, { accepted: true, commit: 'drychk', user_items: [] })
      if (!check) return { status: 'stopped', at: 'check', reason: 'the editor returned nothing', ruling, commits }
      if (check.commit) commits.push(check.commit)
      if (!check.accepted) { status = 'not accepted'; left = check.left || '' }
      log(`Check: ${check.accepted ? 'accepted' : 'not accepted'}`)
    }
  }
}

return {
  status,
  left,
  commits,
  totals: { change: ch.totals || '', after_fixes: fx ? (fx.totals || '') : '' },
  reports: FILES,
  verdicts: { audit: audit.verdict, referee: ref.verdict, editor: ruling ? ruling.decision : 'no findings, no ruling', check: check ? (check.accepted ? 'accepted' : 'not accepted') : '' },
  owner_items: [...(ch.owner_items || []), ...(ruling ? (ruling.user_items || []) : []), ...(check ? (check.user_items || []) : [])],
  outside_the_change: [...(audit.outside || []), ...(ref.outside || [])],
  uncommitted: fx ? [] : [FILES.audit, FILES.referee, ...(ruling ? [FILES.editor] : [])],
}
