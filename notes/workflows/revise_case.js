export const meta = {
  name: 'revise-case',
  description: 'One revision of an accepted case, unattended: the author re-estimates, three referees read the model before any document is written (the check against the owner\'s principles, the economics referee and the audit), the author writes, the audit reads any change the writing made to the model, its inputs or the estimates, the documents referee checks the results and the documents against the model read and the editor rules, and fixes and checks run for at most two rounds. With firstUpgrade, only the fixes and checks of a case\'s first upgrade, from the editor\'s ruling.',
  phases: [
    { title: 'Re-estimate', detail: 'a fresh author: the model, the response letter, a one-page outline' },
    { title: 'Read the model', detail: 'the check against the owner\'s principles, the economics referee and the audit, in parallel' },
    { title: 'Write', detail: 'a fresh author: findings answered, the three documents, the byline' },
    { title: 'Audit the change', detail: 'only where the documents pass changed the model, its inputs or the estimates: the audit reads that diff' },
    { title: 'Review', detail: 'the documents referee: reruns from the re-estimation\'s commit, the results and the documents' },
    { title: 'Rule', detail: 'the editor' },
    { title: 'Fix and check', detail: 'at most two rounds' },
  ],
}

// ARGS {dry?, root, caseDir, caseName, caseLine, stem, toolCommit, accepted, authorTask, writeTask, rulings}
//   dry        true: every seat only reports who it is and whether the files its task names exist, on a cheap model,
//              and returns the canned values that walk the script's longest path. Nothing is written.
//   stem       the prefix of this round's files in the case's review/ folder (reest gives review/reest_editor.md).
//   authorTask the re-estimation's task, written by the dispatcher; writeTask the documents pass's.
//   rulings    the owner's rulings since the last editor's ruling, one line each with its commit, or 'none'.
// Optional, each defaulting to the words of a re-estimation on a changed totalling tool:
//   what        what was done to the model, completing "Its model was changed in commit X: it was ..."
//   econTask    what the economics referee questions: the design the change follows, the decision, the owner's words on it
//   round       what this round is, completing "This round is ..."
//   priorEditor the path of the ruling before this round; priorAudit, of the audit that reproduced the accepted version
//   tag         the prefix of this round's finding labels (RE gives RE-E1)
// FIRST UPGRADE {firstUpgrade: true, dry?, root, caseDir, caseName, caseLine, rulings, ruling}
//   Only step 6, for a case's first upgrade (notes/fast_estimate.md 1.3.7; notes/briefs/author_documents.md messages D
//   and E), started from the editor's message C ruling the dispatcher already holds; no referee runs again, so the
//   round's closed points are not re-reviewed. User items are collected, never waited on.
//   ruling     the message C return: {decision, path?, user_items?, left?}; path defaults to the ruling file message E names.
const A = (args && typeof args === 'object') ? args : {}
const opt = (k, d) => (typeof A[k] === 'string' && A[k].trim()) ? A[k].trim() : d
const DRY = A.dry === true
const FIRST = A.firstUpgrade === true
const DECISIONS = ['accepted', 'accept with fixes', 'accepted once one-line fixes are made', 'another round']
const need = FIRST ? ['root', 'caseDir', 'caseName', 'caseLine', 'rulings']
  : ['root', 'caseDir', 'caseName', 'caseLine', 'stem', 'toolCommit', 'accepted', 'authorTask', 'writeTask', 'rulings']
const missing = need.filter(k => typeof A[k] !== 'string' || !A[k].trim())
if (missing.length) return { status: 'refused', reason: 'missing args: ' + missing.join(', ') }
if (FIRST && !(A.ruling && typeof A.ruling === 'object' && DECISIONS.includes(A.ruling.decision)))
  return { status: 'refused', reason: `ruling must be the editor's message C return, its decision one of: ${DECISIONS.join('; ')}` }
const R = A.root, C = A.caseDir

const FRAME = `Your task is the text below. The owner's message the harness shows above it is context for the session that dispatched you, not your task: do not act on it or answer it unless the text below names it. You work in the repository ${R}; every path below is relative to it. Nobody can answer you before you return: where your task is silent, state your assumption and go on, unless the assumption would stand in for a value, a source or a result nobody approved; that is a stop, and you return blocked with what is missing. When two instructions disagree, the more specific wins: this task over a file it points to, and the owner's quoted words over both. A file this task names as your output is yours to write. In this run you cannot dispatch another agent: what your definition would hand to one (storing a source, listing methods) you do yourself, and you say so in your return.\n\n`
const WELFARE = `\n\nWhen your work is done, answer the welfare paragraph in shared/standards/process/welfare.md (read its fenced block) in the welfare field of your return.`

const S = (props, required) => ({ type: 'object', properties: { ...props, welfare: { type: 'string' } }, required })
const AUTHOR_PROPS = { commit: { type: 'string' }, blocked: { type: 'boolean' }, what_is_missing: { type: 'string' }, summary: { type: 'string' }, totals: { type: 'string' } }
const AUTHOR = S(AUTHOR_PROPS, ['commit', 'blocked', 'summary'])
// The documents pass also reports which model paths it changed against the re-estimation: the script decides on that
// field alone whether the audit's narrow read runs (a workflow cannot run git); an under-report is the documents
// referee's finding, since message B has it diff those paths itself.
const WRITER = S({ ...AUTHOR_PROPS, model_paths: { type: 'array', items: { type: 'string' } } }, ['commit', 'blocked', 'summary', 'model_paths'])
const pathsOf = r => Array.isArray(r.model_paths) ? r.model_paths.filter(p => typeof p === 'string' && p.trim()) : []
const REPORT = S({ verdict: { type: 'string' }, path: { type: 'string' }, gravest: { type: 'array', items: { type: 'string' } } }, ['verdict', 'path', 'gravest'])
const PURPOSE = S({ verdict: { type: 'string', enum: ['write', 'write after these fixes', 'stop for the owner'] }, path: { type: 'string' }, gravest: { type: 'array', items: { type: 'string' } }, owner_items: { type: 'array', items: { type: 'string' } } }, ['verdict', 'path', 'gravest', 'owner_items'])
const RULING = S({ decision: { type: 'string', enum: DECISIONS }, path: { type: 'string' }, user_items: { type: 'array', items: { type: 'string' } }, left: { type: 'string' } }, ['decision', 'path', 'user_items'])

async function seat(type, label, ph, text, schema, dryValue) {
  if (DRY) {
    const p = `DRY RUN of a workflow. Do none of the work the text below describes and write no file. Answer in the summary, verdict or left field (whichever your return has), in under 120 words: (1) the agent type you are, from your own instructions; (2) the model you run on, if you can tell; (3) for each file or folder path the text names as something to read, whether it exists (one ls); (4) the files the text would have you write. Fill the other fields of your return with exactly these values: ${JSON.stringify(dryValue)}. Leave welfare empty.\n\n--- THE TEXT ---\n` + text
    return agent(p, { label: `dry ${label}`, phase: ph, schema, agentType: type, model: 'haiku', effort: 'low' })
  }
  return agent(FRAME + text + WELFARE, { label, phase: ph, schema, agentType: type })
}

const CASE = `The case is ${C} (${A.caseLine}). Its index is ${C}/CASE.md.`
const WHAT = opt('what', 're-estimated on a totalling tool that now draws each factor by a named form')
const ECON_TASK = opt('econTask', `The design it follows is the header of tools/estimate_total.py with the table notes/factor_forms.md.\n\nThe decision to question: how each effect of uncertain sign was re-estimated, and the form named for each factor. For each such effect: whether the rule (a direction that is one fact we do not know is one effect, wholly one direction in each draw; a chance that plays out each time is two rows) is applied rightly; whether its low, middle and high are sourced and are what the source supports as 5th, 50th and 95th percentiles; whether the form fits the quantity; whether anything of uncertain sign was zeroed, made symmetric for convenience, bounded or left out of the total or of the ranking of inputs. The owner's words on this: "Many effects in CBA have an uncertain sign and we should never have any rule that an unknown effect cannot change a sign"; "anything like that with large effects based on the draw should never be zeroed out or ignored, you highlight it and talk about it in the voi calculation". Then the forms of the ten factors with the largest share of each design's variance.`)
const ROUND = opt('round', 'the case\'s re-estimation on the changed totalling tool, after an accepted milestone 2')
const PRIOR_EDITOR = opt('priorEditor', `${C}/review/m2_r1_editor.md`)
const PRIOR_AUDIT = opt('priorAudit', `${C}/review/m2_r2_audit.md if it exists, else ${C}/review/m2_audit.md`)
const TAG = opt('tag', 'RE')
const MODEL_PATHS = `${C}/model ${C}/inputs.toml ${C}/estimates.toml`

// The narrow audit read: one audit-referee read of the diff from..to on the model paths, against the method accepted
// before it; null when the author named no changed model path.
async function auditDiff(ph, label, from, to, changed, accepted, account, report, tag) {
  if (!changed.length) return null
  return seat('audit-referee', label, ph,
    `${CASE} The model, its inputs or the estimates were changed between commit ${from} and commit ${to}, after the audit had read the model; the author names these paths: ${changed.join(', ')}. Read that change alone: run \`git diff ${from} ${to} -- ${MODEL_PATHS}\` (the paths the case has) and audit that diff by your definition against ${accepted}, and nothing else: each change declared in ${account}, each changed number traced to its stored source, each changed estimate's arithmetic redone, and, where a change moves a total, the totalling tool rerun at commit ${to} in a copy under your scratchpad directory, never in the case's own folder, its totals compared with the author's account. A change in the diff the author did not name is a finding. The documents are not yours to read. Number your findings ${tag}1 onward. Write your report to ${report} and to no other file; do not commit. Return the verdict, the three gravest findings one line each, and the path.`,
    REPORT, { verdict: 'accept', path: report, gravest: [] })
}

// Fixes and checks after an editor's ruling, two rounds at most (author_documents.md messages D and E; editor_ruling.md
// message A, item 6.1). A fresh author and a fresh editor each time: a workflow resumes no seat. rec: {record, response,
// editor, auditFix (the prefix of each fix's audit report)}. A fix that changes a model path gets the narrow audit read
// before the editor's check; a one-line fix that does so is checked by the editor too, rather than accepted unread.
// Returns {stop} on an early return, else {ruling, rounds}.
async function fixAndCheck(start, commits, rec) {
  phase('Fix and check')
  let ruling = start, rounds = 0
  while (ruling.decision !== 'accepted' && ruling.decision !== 'another round' && rounds < 2) {
    rounds += 1
    const oneLine = ruling.decision === 'accepted once one-line fixes are made'
    const base = commits.length ? commits[commits.length - 1] : 'the commit HEAD was at when you began'
    const fix = await seat('case-author', `author: fixes ${rounds}`, 'Fix and check',
      `${CASE}\n\nYour task is MESSAGE D of notes/briefs/author_documents.md: read that file from the MESSAGE D marker to the next marker and follow it. You are a fresh author: the round's record is ${rec.record}, and the editor's ruling, with any check appended, is ${rec.editor}. The editor has ruled on this round: ${ruling.decision}. Make the fixes the ruling${rounds > 1 ? "'s latest check" : ''} lists, and no other change; answer in ${rec.response} where message D says the response letter. Commit once, with your Co-Authored-By line. Return the commit; in the summary, one line on each fix saying that it is made; and in model_paths every path that \`git diff --name-only ${base} <your commit> -- ${MODEL_PATHS}\` prints, an empty list if it prints none. A change there is declared in ${rec.response} and is read by the audit before the editor's check.`,
      WRITER, { commit: `dryfix${rounds}`, blocked: false, model_paths: rounds === 1 ? [`${C}/model`] : [] })
    if (!fix) return { stop: { status: 'stopped', at: `fixes ${rounds}`, reason: 'the author returned nothing', ruling, rounds, commits } }
    if (fix.blocked) return { stop: { status: 'blocked', at: `fixes ${rounds}`, author: fix, ruling, rounds, commits } }
    const from = commits.length ? commits[commits.length - 1] : `${fix.commit}~1`
    commits.push(fix.commit)
    const fixAudit = await auditDiff('Fix and check', `audit referee: fixes ${rounds}`, from, fix.commit, pathsOf(fix),
      `the method the editor's ruling ${rec.editor} accepted`, rec.response, `${rec.auditFix}${rounds}.md`, `${TAG}-AF${rounds}-`)
    if (pathsOf(fix).length && !fixAudit) return { stop: { status: 'stopped', at: `audit of fixes ${rounds}`, reason: 'the audit referee returned nothing', ruling, rounds, commits } }
    if (fixAudit) log(`Audit of fixes ${rounds}: ${fixAudit.verdict}`)
    if (oneLine && !fixAudit) { ruling = { ...ruling, decision: 'accepted', left: '' }; break }
    const AUDIT_READ = fixAudit ? ` The fixes changed the model, its inputs or the estimates, and the audit has read that diff alone: ${rec.auditFix}${rounds}.md (verdict: ${fixAudit.verdict}); rule on its findings with the rest.` : ''
    const check = await seat('editor', `editor: check ${rounds}`, 'Fix and check',
      `Your task is MESSAGE E of notes/briefs/author_documents.md: read that file from the MESSAGE E marker to the next marker and follow it, with notes/briefs/editor_ruling.md message A item 6.1 as it cites. You are a fresh editor checking another's ruling: it is ${rec.editor}; read it whole first. The case is ${A.caseName} (${A.caseLine}); the author's fixes are in commit ${fix.commit}.${AUDIT_READ} The rulings the user or the owner has made on the case since the ruling, each with its commit: ${A.rulings}. Append your check to ${rec.editor} in place of the path the message names, and commit that file and ${C}/review/points.toml alone with your Co-Authored-By line. Return your final line as the decision (accepted; accepted once one-line fixes are made; or, if something is left that is more than that, accept with fixes), what is left in the left field, any new item that is the user's, and the path.`,
      RULING, rounds === 1
        ? { decision: 'accepted once one-line fixes are made', path: rec.editor, user_items: [], left: 'dry: one sentence' }
        : { decision: 'accepted', path: rec.editor, user_items: [], left: '' })
    if (!check) return { stop: { status: 'stopped', at: `check ${rounds}`, reason: 'the editor returned nothing', ruling, rounds, commits } }
    ruling = { ...check, user_items: [...(ruling.user_items || []), ...(check.user_items || [])] }
    log(`Check ${rounds}: ${ruling.decision}`)
  }
  return { ruling, rounds }
}
const statusOf = d => d === 'accepted' ? 'accepted' : (d === 'another round' ? 'another round' : 'not accepted after two rounds')

// The first upgrade: the loop alone, from the editor's message C ruling.
if (FIRST) {
  const start = { ...A.ruling, user_items: Array.isArray(A.ruling.user_items) ? A.ruling.user_items : [] }
  const editorFile = (typeof start.path === 'string' && start.path.trim()) ? start.path.trim() : `${C}/review/m2_r1_editor.md`
  const response = 'the response letter that MESSAGE D of notes/briefs/author_documents.md names'
  const commits = []
  const L = await fixAndCheck(start, commits, {
    record: `the round's reports and ruling, which message D names`, response, editor: editorFile,
    auditFix: editorFile.replace(/(_editor)?\.md$/, '') + '_audit_fix',
  })
  if (L.stop) return { ...L.stop, owner_items: L.stop.ruling.user_items || [] }
  return {
    status: statusOf(L.ruling.decision), left: L.ruling.left || '', rounds: L.rounds, commits,
    ruling: editorFile, owner_items: L.ruling.user_items || [],
  }
}

const REV = `${C}/review/${A.stem}`
const FILES = {
  response: `${REV}_r1_response.md`, outline: `${REV}_outline.md`, purpose: `${REV}_purpose.md`, econ: `${REV}_econ.md`,
  audit: `${REV}_audit.md`, auditChange: `${REV}_audit_change.md`, documents: `${REV}_documents.md`, editor: `${REV}_editor.md`,
}

// 1. The re-estimation.
phase('Re-estimate')
// args.prior {a1, purpose, econ, audit}: the returns of steps 1 and 2 from an earlier run of this chain, to start at the documents pass.
const a1 = (A.prior && A.prior.a1) ? A.prior.a1 : await seat('case-author', 'author: re-estimation', 'Re-estimate',
  `${CASE}\n\n${A.authorTask}\n\nWrite the response letter as its template, ${REV}_r1_response_template.md (notes/briefs/response_letter_template.md), which the case's documents script fills into ${FILES.response} (run it before you commit), and write the one-page outline to ${FILES.outline}. Return: the commit, each design's expected net benefits before and after each change in the totals field, and a summary of what moved and why.`,
  AUTHOR, { commit: 'dry0001', blocked: false, totals: 'dry' })
if (!a1) return { status: 'stopped', at: 'Re-estimate', reason: 'the author returned nothing' }
if (a1.blocked) return { status: 'blocked', at: 'Re-estimate', author: a1 }
log(`Re-estimated at ${a1.commit}`)

// 2. Three readers of the model, before any document is written: the audit reads commit a1 alone.
phase('Read the model')
const [purpose, econ, audit] = (A.prior && A.prior.purpose && A.prior.econ && A.prior.audit)
  ? [A.prior.purpose, A.prior.econ, A.prior.audit] : await parallel([
  () => seat('referee', 'referee: the owner\'s principles', 'Read the model',
    `Your task is the standing brief notes/briefs/purpose_check.md: read that file and follow the text below its marker line "=== BRIEF ===", with its three fields filled so: [[case folder]] is ${C}; [[outline]] is ${FILES.outline}; [[report]] is ${FILES.purpose}. The case: ${A.caseLine}. Its model was changed in commit ${a1.commit}: it was ${WHAT}. The author's account is ${FILES.response}. Write your report to ${FILES.purpose} and to no other file; do not commit. Return the verdict in the brief's words, the three gravest findings one line each, every item you mark as the owner's, and the path.`,
    PURPOSE, { verdict: 'write after these fixes', path: FILES.purpose, gravest: ['dry'], owner_items: ['dry owner item'] }),
  () => seat('referee', 'referee: the re-estimated effects', 'Read the model',
    `${CASE} Its accepted model was changed in commit ${a1.commit}: it was ${WHAT} (the totalling tool is at commit ${A.toolCommit}). The author's account is ${FILES.response}. ${ECON_TASK} Number your findings ${TAG}-E1 onward, rank them by how far each could move a design's expected net benefits, and give one verdict. Write your report to ${FILES.econ} and to no other file; do not commit. Name each source you fetched, with its address, in your return. Return the verdict, the three gravest findings one line each, and the path.`,
    REPORT, { verdict: 'sound with changes', path: FILES.econ, gravest: ['dry'] }),
  () => seat('audit-referee', 'audit referee', 'Read the model',
    `${CASE} Audit its re-estimation, before any document is rewritten: the model re-estimated in commit ${a1.commit}; the accepted version before it is commit ${A.accepted}, whose results an earlier audit reproduced (${PRIOR_AUDIT}). The author's account is ${FILES.response}, with its matrix of findings answered.\n\nAudit by your definition, on what changed: every factor of every re-estimated effect traced to its stored source; the arithmetic of each re-estimated estimate redone; the totalling tool rerun on the case's tables at commit ${a1.commit} and each design's total, range and share of draws above zero compared with the author's account; the author's table of each design's total before and after each change checked step by step. The documents are rewritten after your report and are not yours to read. Run with ${R}/.venv/bin/python and the tools of ${R}/tools/, never writing in the case's own folder: the total tool with --out a folder of your own under your scratchpad directory; a model writes beside itself, so where there is one, copy ${C} there with the draws files its tables name and run the model and the tool on the copy. Number your findings ${TAG}-A1 onward. Write your report to ${FILES.audit} and to no other file; do not commit. Return the verdict, the three gravest findings one line each, and the path.`,
    REPORT, { verdict: 'accept', path: FILES.audit, gravest: [] }),
])
if (!purpose || !econ || !audit) return { status: 'stopped', at: 'Read the model', reason: 'a referee returned nothing', purpose, econ, audit, author: a1 }
// args.ownerRuled: a sentence saying where the owner's ruling, or the default held until he rules, is recorded; with it the chain goes on past the stop.
const RULED = (typeof A.ownerRuled === 'string' && A.ownerRuled.trim()) ? A.ownerRuled.trim() : ''
if (purpose.verdict === 'stop for the owner' && !RULED) return { status: 'stop for the owner', at: 'Read the model', purpose, econ, audit, author: a1 }
log(`Principles check: ${purpose.verdict}. Economics referee: ${econ.verdict}. Audit: ${audit.verdict}`)

// 3. The documents pass.
phase('Write')
const a2 = await seat('case-author', 'author: findings and documents', 'Write',
  `${CASE}\n\nYou are a fresh author taking the case from its re-estimation (commit ${a1.commit}; the account is ${FILES.response}, the outline ${FILES.outline}). Three referees have read the re-estimated model before any document is rewritten: ${FILES.purpose} (the check against the owner's principles; verdict: ${purpose.verdict}${RULED ? '; ' + RULED : ''}), ${FILES.econ} (the economics referee; verdict: ${econ.verdict}) and ${FILES.audit} (the audit; verdict: ${audit.verdict}).\n\n${A.writeTask}\n\nItems the principles check marks as the owner's are not yours to settle: leave the documents as the accepted version has them on each, and list them in your return. Return: the commit, each design's expected net benefits if any finding moved them (before and after, by finding) in the totals field, a summary: each finding answered in one line, the summary's page count and the paper's; and in model_paths every path that \`git diff --name-only ${a1.commit} <your commit> -- ${MODEL_PATHS}\` prints, an empty list if it prints none. A change there is declared in ${FILES.response} and is read by the audit before the documents are reviewed.`,
  WRITER, { commit: 'dry0002', blocked: false, totals: 'dry', model_paths: [`${C}/model`] })
if (!a2) return { status: 'stopped', at: 'Write', reason: 'the author returned nothing', purpose, econ, audit }
if (a2.blocked) return { status: 'blocked', at: 'Write', author: a2, purpose, econ, audit }
log(`Documents written at ${a2.commit}`)

// 3a. Where the documents pass changed the model, its inputs or the estimates after the audit read a1, the audit reads
// that diff alone before the documents are reviewed (notes/briefs/author_documents.md, message B, 1); else nothing runs.
const changed = pathsOf(a2)
let auditChange = null
if (changed.length) {
  phase('Audit the change')
  auditChange = await auditDiff('Audit the change', 'audit referee: the change after a1', a1.commit, a2.commit, changed,
    `the method accepted at ${a1.commit}, which you audited (${FILES.audit})`, FILES.response, FILES.auditChange, `${TAG}-AC`)
  if (!auditChange) return { status: 'stopped', at: 'Audit the change', reason: 'the audit referee returned nothing', audit, commits: [a1.commit, a2.commit] }
  log(`Audit of the change: ${auditChange.verdict}`)
}
const CHANGE_READ = auditChange
  ? ` The economics referee and the principles check have not seen it; the audit has read that diff alone: ${FILES.auditChange} (verdict: ${auditChange.verdict}).`
  : ` The author named no changed path there, so no narrow audit read ran: no reader, the audit included, has seen a change there, and your diff is the only check on it.`

// 4. The documents review: the results and the documents, against the model the three readers read (commit a1).
phase('Review')
const docs = await seat('documents-referee', 'documents referee', 'Review',
  `Your task is MESSAGE B of notes/briefs/author_documents.md: read that file from the MESSAGE B marker to the next marker and follow it, with its fields filled so: the case is ${A.caseName} (${A.caseLine}); the commit is ${a2.commit}; the M1 commit, the model the readers reviewed, from which you rerun and diff, is the re-estimation's commit ${a1.commit}; the response letter that holds the matrix is ${FILES.response}. This is a revision of documents accepted at commit ${A.accepted}. A change to the model, the inputs or the estimates between ${a1.commit} and ${a2.commit} that the author made in answer to the readers' findings is declared in ${FILES.response}: check each against it, and list each in your report.${CHANGE_READ} Review the results and the documents for faithfulness, with most care what this round changed (the outline of what they should now say is ${FILES.outline}). In place of the report path the message names, write your report to ${FILES.documents}, and number your findings ${TAG}-D1 onward. Do not commit.`,
  REPORT, { verdict: 'minor revision', path: FILES.documents, gravest: ['dry'] })
if (!docs) return { status: 'stopped', at: 'Review', reason: 'the documents referee returned nothing', audit, commits: [a1.commit, a2.commit] }
log(`Documents: ${docs.verdict}`)

// 5. The editor.
phase('Rule')
const EDITOR_C = `Your task is MESSAGE C of notes/briefs/author_documents.md: read that file from the MESSAGE C marker to the next marker and follow it, with notes/briefs/editor_ruling.md message A item 6.1 as it cites. Its fields: the case is ${A.caseName} (${A.caseLine}); the author's commit is ${a2.commit}; the response letter is ${FILES.response}. This round is ${ROUND} (your predecessor's ruling is ${PRIOR_EDITOR}). The reports to rule on are ${auditChange ? 'five' : 'four'}: ${FILES.purpose} (the check against the owner's principles, read before the documents were rewritten), ${FILES.econ} (the economics referee on the changed model, likewise), ${FILES.audit} (the audit of the changed model, likewise)${auditChange ? `, ${FILES.auditChange} (the audit of the change the documents pass made to the model, its inputs or the estimates)` : ''} and ${FILES.documents} (the documents referee, on the results and the documents). The rulings the user or the owner has made on the case since that ruling, each with its commit: ${A.rulings}. In place of the path the message names, write your ruling to ${FILES.editor}; do not commit. Return your decision on the whole in one of the four forms your return offers, every item that is the user's to decide (each complete in one or two plain sentences with its options), and the path.`
let ruling = await seat('editor', 'editor: ruling', 'Rule', EDITOR_C, RULING,
  { decision: 'accept with fixes', path: FILES.editor, user_items: ['dry user item'] })
if (!ruling) return { status: 'stopped', at: 'Rule', reason: 'the editor returned nothing', audit, docs, commits: [a1.commit, a2.commit] }
log(`Editor: ${ruling.decision}`)

// 6. Fixes and checks, two rounds at most.
const commits = [a1.commit, a2.commit]
const L = await fixAndCheck(ruling, commits, {
  record: `${FILES.response} (the author's account)`, response: FILES.response, editor: FILES.editor, auditFix: `${REV}_audit_fix`,
})
if (L.stop) return L.stop
ruling = L.ruling

return {
  status: statusOf(ruling.decision),
  left: ruling.left || '',
  rounds: L.rounds,
  commits,
  totals: { re_estimation: a1.totals || '', after_findings: a2.totals || '' },
  reports: FILES,
  verdicts: { purpose: purpose.verdict, econ: econ.verdict, audit: audit.verdict, ...(auditChange ? { audit_change: auditChange.verdict } : {}), documents: docs.verdict },
  owner_items: [...(purpose.owner_items || []), ...(ruling.user_items || [])],
  uncommitted: 'the referees and the editor\'s first ruling do not commit: the dispatcher commits the review files',
}