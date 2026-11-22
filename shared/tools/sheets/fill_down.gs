/**
 * Fill down: when a cell of the first draw row is edited, its formula is pasted down its column's other draw rows,
 * so every draw of a column is computed by the same formula.
 *
 * Bound to a Monte Carlo sheet (Extensions > Apps Script) whose column A reads "Graph" in the row above the draws
 * and numbers the draws from 1. onEdit is a simple trigger: it needs no authorization, changes only this file, and a
 * copy of the file carries it. It runs on an edit a person makes, not on one made through the Sheets API, and not
 * for a reader with view-only access.
 *
 * It acts only on an edit that lies wholly in the first draw row of such a tab, wherever that row is: tabs with
 * more header rows start their draws lower. An edit that spans several rows (a pasted column of values) is left as
 * the person made it, and an array formula (ARRAYFORMULA, ARRAY_CONSTRAIN), which fills its column itself, is never
 * pasted down.
 */
var HEADER_ROWS_SEARCHED = 40;

function onEdit(e) {
  if (!e || !e.range) return;
  var range = e.range;
  if (range.getRow() !== range.getLastRow() || range.getRow() > HEADER_ROWS_SEARCHED + 1) return;
  var sheet = range.getSheet();
  var first = firstDrawRow_(sheet);
  if (range.getRow() !== first) return;
  var lastDraw = lastDrawRow_(sheet, first);
  if (lastDraw <= first) return;
  var firstColumn = Math.max(range.getColumn(), 2);
  var formulas = sheet.getRange(first, firstColumn, 1, range.getLastColumn() - firstColumn + 1).getFormulas()[0];
  for (var i = 0; i < formulas.length; i++) {
    if (/^=\s*(ARRAYFORMULA|ARRAY_CONSTRAIN)\s*\(/i.test(formulas[i])) continue;
    sheet.getRange(first, firstColumn + i)
        .copyTo(sheet.getRange(first + 1, firstColumn + i, lastDraw - first, 1),
            SpreadsheetApp.CopyPasteType.PASTE_FORMULA, false);
  }
}

/** The row under column A's "Graph" where that row is draw 1, or 0 on a tab with no such rows. */
function firstDrawRow_(sheet) {
  var rows = Math.min(sheet.getMaxRows(), HEADER_ROWS_SEARCHED + 1);
  var labels = sheet.getRange(1, 1, rows, 1).getValues();
  for (var i = 0; i + 1 < labels.length; i++) {
    if (labels[i][0] === 'Graph') return labels[i + 1][0] === 1 ? i + 2 : 0;
  }
  return 0;
}

/** The last row that column A numbers as a draw. */
function lastDrawRow_(sheet, first) {
  var numbers = sheet.getRange(first, 1, sheet.getMaxRows() - first + 1, 1).getValues();
  var last = first;
  for (var i = 0; i < numbers.length; i++) {
    if (typeof numbers[i][0] === 'number') last = first + i;
  }
  return last;
}
