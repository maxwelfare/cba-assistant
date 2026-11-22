export const meta = {
  name: 'case-edition-and-layout',
  description: 'After a case\'s plain documents are accepted: the layout review of the plain PDFs, the edition for one named audience, its one review round, its layout, and the mechanical checks once more.',
  phases: [
    { title: 'Lay out the plain documents', detail: 'pdf-layout reviews; findings of content go to a fresh author, then a second look; findings of the typesetter go back to the dispatching seat for a build of the generator' },
    { title: 'Re-voice', detail: 'the audience translator, from the profile' },
    { title: 'Review the edition', detail: 'the documents referee, then the editor; one round' },
    { title: 'Fix and check', detail: 'the translator\'s fixes and the editor\'s check' },
    { title: 'Lay out the edition', detail: 'pdf-layout reviews the edition\'s PDFs, then the mechanical checks again' },
  ],
}

// ARGS {dry?, root, caseDir, caseName, caseLine, key, plainCommit, resultsFile, rulings}
const A = (args && typeof args === 'object') ? args : {}
const DRY = A.dry === true
const need = ['root', 'caseDir', 'caseName', 'caseLine', 'key', 'plainCommit', 'resultsFile', 'rulings']
const missing = need.filter(k => typeof A[k] !== 'string' || !A[k].trim())
if (missing.length) return { status: 'refused', reason: 'missing args: ' + missing.join(', ') }
const R = A.root, C = A.caseDir, N = A.caseName, K = A.key
const ED = `${C}/documents/audience/${K}`
const FAITH = `${C}/review/audience_${K}_faithfulness.md`, RUL = `${C}/review/audience_${K}_editor.md`

// An optional page notice (args.notice): the typesetter prints it only when its option is passed, so every seat that builds is told.
const NOTICE = (typeof A.notice === 'string' && A.notice.trim()) ? A.notice.trim() : ''
const NOTICE_LINE = NOTICE ? ` Every page of every document of this case carries the notice "${NOTICE}" at its head (the owner, 2026-11-12: \"put a notice like 'draft unreviewed' in each page in the header and/or footer\"; "at its head" is the seat's choice of the header). The typesetter prints it only when its option is passed, so every build of the case's PDFs in this run is \`.venv/bin/python tools/typeset.py --notice "${NOTICE}" ${C}\`, wherever your definition, a brief or a checklist gives the build command without the option; a PDF without the notice on every page is not finished. The notice is not a word of the documents: leave it out of every count and comparison of their text.` : ''
const FRAME = `Your task is the text below. The owner's message the harness shows above it is context for the session that dispatched you, not your task: do not act on it or answer it unless the text below names it. You work in the repository ${R}; every path below is relative to it. Nobody can answer you before you return: where your task is silent, state your assumption and go on, unless the assumption would stand in for a value, a source or a result nobody approved; that is a stop, and you return blocked with what is missing. When two instructions disagree, the more specific wins: this task over a file it points to, and the owner's quoted words over both. A file this task names as your output is yours to write. In this run you cannot dispatch another agent, and no seat is resumed: where a brief says "resumed", you are a fresh seat reading the record the task names.${NOTICE_LINE}\n\n`
const WELFARE = `\n\nWhen your work is done, answer the welfare paragraph in shared/standards/process/welfare.md (read its fenced block) in the welfare field of your return.`
const S = (props, required) => ({ type: 'object', properties: { ...props, welfare: { type: 'string' } }, required })
const LAYOUT = S({ reviewed: { type: 'string' }, blocked: { type: 'boolean' }, author_findings: { type: 'array', items: { type: 'string' } }, template_findings: { type: 'array', items: { type: 'string' } }, left: { type: 'string' }, summary: { type: 'string' } }, ['reviewed', 'blocked', 'author_findings', 'template_findings', 'summary'])
const WORK = S({ commit: { type: 'string' }, blocked: { type: 'boolean' }, what_is_missing: { type: 'string' }, summary: { type: 'string' } }, ['commit', 'blocked', 'summary'])
const REPORT = S({ verdict: { type: 'string' }, path: { type: 'string' }, gravest: { type: 'array', items: { type: 'string' } }, checks: { type: 'string' } }, ['verdict', 'path', 'gravest'])
const RULING = S({ decision: { type: 'string', enum: ['accept', 'accept with fixes'] }, path: { type: 'string' }, fixes: { type: 'array', items: { type: 'string' } }, plain_edition_points: { type: 'array', items: { type: 'string' } }, user_items: { type: 'array', items: { type: 'string' } } }, ['decision', 'path', 'fixes', 'user_items'])
const CHECK = S({ accepted: { type: 'boolean' }, left: { type: 'string' }, commit: { type: 'string' } }, ['accepted', 'left', 'commit'])
const RUN = S({ output: { type: 'string' }, pages: { type: 'string' }, findings: { type: 'array', items: { type: 'string' } } }, ['output', 'pages', 'findings'])

async function seat(type, label, ph, text, schema, dryValue, opts) {
  if (DRY) {
    const p = `DRY RUN of a workflow. Do none of the work the text below describes and write no file. In the summary, verdict, left or output field (whichever your return has), in under 100 words, say: for each file or folder path the text names as something to read, whether it exists (one ls). Fill the other fields of your return with exactly these values: ${JSON.stringify(dryValue)}. Leave welfare empty.\n\n--- THE TEXT ---\n` + text
    return agent(p, { label: `dry ${label}`, phase: ph, schema, agentType: type, model: 'haiku', effort: 'low' })
  }
  return agent(FRAME + text + WELFARE, { label, phase: ph, schema, agentType: type, ...(opts || {}) })
}

const CASE = `The case is ${C} (${A.caseLine}).`
const commits = []

// 1. The plain documents' layout review (pdf-layout is review-only: it changes no file and commits nothing). Its
// findings of content go to an author once, then a second look; its findings of the typesetter or its format are
// returned to the dispatching seat, which sends them to a build of the generator and rebuilds the PDFs, since a fault
// of a generated output is fixed in its generator, never in the output.
const templateFindings = []
phase('Lay out the plain documents')
const layoutText = (round) => `${CASE} Review the layout of its three typeset documents (the one-page summary, the policy paper, the technical appendix in ${C}/documents/), by your definition and its checklist notes/pdf_layout_review.md. The documents' content was accepted at commit ${A.plainCommit}${round > 1 ? '; an author has since made the content fixes your first review asked for, and this is the look after them (checklist 7.1)' : ''}. Leave ${ED}/ alone if it exists: the audience edition has its own review. You change no file and commit nothing. Return: in reviewed, the commit you reviewed; in author_findings, each finding that is the author's (a fault of content: a word, a number, a claim, a figure's code), one line each with its file and place, and an empty list if none; in template_findings, each fault of the typesetter or its format (tools/typeset.py, tools/house_format/), one line each with the document, the page and what is wrong, and an empty list if none; in left, what is left and why; in summary, the measures of each document.`
let lay = await seat('pdf-layout', 'layout: plain', 'Lay out the plain documents', layoutText(1), LAYOUT,
  { reviewed: 'drylay1', blocked: false, author_findings: ['dry: a chart label is cut'], template_findings: [], left: '' })
if (!lay) return { status: 'stopped', at: 'layout of the plain documents', reason: 'the seat returned nothing' }
if (lay.blocked) return { status: 'blocked', at: 'layout of the plain documents', layout: lay }
templateFindings.push(...lay.template_findings)
let plain = A.plainCommit
if (lay.author_findings.length) {
  const fix = await seat('case-author', 'author: layout findings', 'Lay out the plain documents',
    `${CASE} You are a fresh author. The layout reviewer looked at the case's typeset documents (commit ${lay.reviewed}) and returned these findings of content, which are the author's to fix:\n\n${lay.author_findings.map((f, i) => `${i + 1}. ${f}`).join('\n')}\n\nMake each, through the templates, the facts script or the figures script, by notes/briefs/author_documents.md message D item 1 (for each prose claim a fix corrects, grep the summary, the paper and the appendix and their templates for every copy and correct each; limits and the review's status are printed from review/points.toml and need no grep) and message A item 7 (build and look). Change no result and no claim's strength; a finding that would is not made, and you say so. The rulings for the round, as the dispatching seat passes them (a ruling of the owner's carries his words and OW id; any other wording is the seat's): ${A.rulings}. Commit with explicit paths and your Co-Authored-By line. Return the commit and one line on each finding.`,
    WORK, { commit: 'dryfixlay', blocked: false })
  if (!fix) return { status: 'stopped', at: 'the author\'s layout findings', reason: 'the seat returned nothing', commits }
  if (fix.blocked) return { status: 'blocked', at: 'the author\'s layout findings', author: fix, commits }
  commits.push(fix.commit)
  plain = fix.commit
  lay = await seat('pdf-layout', 'layout: plain, second look', 'Lay out the plain documents', layoutText(2), LAYOUT,
    { reviewed: 'dryfixlay', blocked: false, author_findings: [], template_findings: [], left: '' })
  if (!lay) return { status: 'stopped', at: 'second look at the plain documents', reason: 'the seat returned nothing', commits }
  templateFindings.push(...lay.template_findings)
}
log(`Plain documents reviewed at ${plain}`)

// 2. The edition.
phase('Re-voice')
const tr = await seat('audience-translator', 'translator', 'Re-voice',
  `The case is ${N} (${A.caseLine}), in ${C}/. The profile's key is ${K} (audiences/${K}.toml). The commit of the plain documents is ${plain}. The commit trailer is "Audience: ${N} ${K} draft". The case's requirements.md says what the case asks its documents to attend to for this reader and wins over the profile. Return as your definition says, with the commit and, in the summary, each document's pages, the summary's body size and the result of M1 to M6.`,
  WORK, { commit: 'drytr1', blocked: false })
if (!tr) return { status: 'stopped', at: 'Re-voice', reason: 'the translator returned nothing', commits }
if (tr.blocked) return { status: 'blocked', at: 'Re-voice', translator: tr, commits }
commits.push(tr.commit)
log(`Edition drafted at ${tr.commit}`)

// 3. One round of review.
phase('Review the edition')
const fills = `its fields filled so: [[case]] is ${N}; [[the case in one sentence: the action, against what]] is "${A.caseLine}"; [[key]] is ${K}; [[commit]] is ${tr.commit}; [[the results file]] is ${A.resultsFile}`
const rep = await seat('documents-referee', 'referee: faithfulness', 'Review the edition',
  `Your task is MESSAGE A of notes/briefs/audience_review.md: read that file from the MESSAGE A marker to the next marker and follow it, with ${fills}. Put the result of M1 to M6 in the checks field of your return.`,
  REPORT, { verdict: 'minor revision', path: FAITH, gravest: ['dry'], checks: 'dry' })
if (!rep) return { status: 'stopped', at: 'the faithfulness review', reason: 'the referee returned nothing', commits }
const rul = await seat('editor', 'editor: ruling on the edition', 'Review the edition',
  `Your task is MESSAGE B of notes/briefs/audience_review.md: read that file from the MESSAGE B marker to the next marker and follow it, with ${fills}; [[verdict]] is "${rep.verdict}". The rulings for the round, as the dispatching seat passes them (a ruling of the owner's carries his words and OW id; any other wording is the seat's): ${A.rulings}. Return your ruling as the decision, each fix one line in fixes, the points in the plain edition and on the profile in plain_edition_points, and the user's items.`,
  RULING, { decision: 'accept with fixes', path: RUL, fixes: ['dry fix'], user_items: [] })
if (!rul) return { status: 'stopped', at: 'the editor\'s ruling on the edition', reason: 'the editor returned nothing', commits, report: rep }
log(`Edition: referee ${rep.verdict}; editor ${rul.decision}, ${rul.fixes.length} fixes`)

// 4. Fixes and the check.
phase('Fix and check')
let check = { accepted: true, left: '', commit: tr.commit }
let edition = tr.commit
if (rul.decision === 'accept with fixes' || rul.fixes.length) {
  const fx = await seat('audience-translator', 'translator: fixes', 'Fix and check',
    `Your task is MESSAGE C of notes/briefs/audience_review.md: read that file from the MESSAGE C marker to the next marker and follow it, with [[case]] as ${N} and [[key]] as ${K}. You are a fresh translator: the edition you fix is in ${ED}/ (drafted in commit ${tr.commit}), with its crosswalk.md. Return the commit and, in the summary, the fixes made, any not made as listed with why, each document's pages and the summary's body size.`,
    WORK, { commit: 'drytr2', blocked: false })
  if (!fx) return { status: 'stopped', at: 'the translator\'s fixes', reason: 'the translator returned nothing', commits, ruling: rul }
  if (fx.blocked) return { status: 'blocked', at: 'the translator\'s fixes', translator: fx, commits }
  commits.push(fx.commit)
  edition = fx.commit
  check = await seat('editor', 'editor: check of the edition', 'Fix and check',
    `Your task is MESSAGE D of notes/briefs/audience_review.md: read that file from the MESSAGE D marker to the next marker and follow it, with [[case]] as ${N}, [[key]] as ${K} and [[commit]] as ${fx.commit}. You are a fresh editor checking another's ruling: it is ${RUL}; read it whole first. Return whether the edition is accepted, what is left, and your commit.`,
    CHECK, { accepted: true, left: '', commit: 'drychk' })
  if (!check) return { status: 'stopped', at: 'the editor\'s check of the edition', reason: 'the editor returned nothing', commits }
  commits.push(check.commit)
}

// 5. The edition's layout, and the mechanical checks once more.
phase('Lay out the edition')
const lay2 = await seat('pdf-layout', 'layout: edition', 'Lay out the edition',
  `${CASE} Review the layout of its audience edition's two PDFs, ${ED}/executive_summary.pdf and ${ED}/policy_paper.pdf (the edition for the profile audiences/${K}.toml, at commit ${edition}), by your definition and its checklist. Your definition's measuring step names documents/*.pdf: for this task measure and render ${ED}/*.pdf instead. You change no file and commit nothing. Return as for any layout review, with findings that are the translator's or the author's in author_findings and those of the typesetter or its format in template_findings.`,
  LAYOUT, { reviewed: 'drylay3', blocked: false, author_findings: [], template_findings: [], left: '' })
if (lay2) templateFindings.push(...lay2.template_findings)
const fin = await seat('general-purpose', 'mechanical checks, once more', 'Lay out the edition',
  `Run commands and report; change no file and commit nothing. In notes/briefs/audience_review.md, MESSAGE A, item 4 holds a block of shell commands (the mechanical checks M1 to M6) with the placeholders [[case]] and [[key]]: run that block from the repository root with [[case]] as ${N} and [[key]] as ${K}, and give its whole output in the output field. Then run "pdfinfo" on each PDF in ${C}/documents/ and ${ED}/ and give each file's page count in the pages field. In findings, list every line of output that items 4.1 to 4.4 of that message call a finding (M1 to M4 only), one line each, or an empty list.${NOTICE ? ` Then check the page notice: for each of those PDFs and each of its pages, run "pdftotext -f N -l N FILE -" and see whether the page's text holds "${NOTICE}" (ignore case and line breaks); add to findings one line "no notice: FILE page N" for each page without it, and say in the pages field how many pages you checked.` : ''}`,
  RUN, { output: 'dry', pages: 'dry', findings: [] }, { model: 'sonnet', effort: 'low' })

return {
  status: check.accepted ? 'edition accepted' : 'edition not accepted',
  left: check.left || '',
  commits,
  plain_documents_commit: plain,
  edition_commit: edition,
  template_findings: templateFindings,
  referee: rep.verdict,
  ruling: rul.decision,
  plain_edition_points: rul.plain_edition_points || [],
  user_items: rul.user_items || [],
  layout_left: { plain: lay.left || '', edition: lay2 ? (lay2.left || '') : 'the layout seat returned nothing', edition_findings: lay2 ? lay2.author_findings : [] },
  checks: fin || 'the runner returned nothing',
}