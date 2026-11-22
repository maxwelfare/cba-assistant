-- Every table's columns left to Typst (auto tracks), in place of pandoc's widths from the dashes of a pipe table's
-- separator line (pandoc manual, "Pipe tables"); the format's header then sizes a table that overflows the line by
-- tabulary's rule and leaves alone one given widths of its own. The size tables are set at is the header's
-- doc-tables, which tools/render.py applies with the document's `table-size`.
function Table(t)
  for i, c in ipairs(t.colspecs) do t.colspecs[i] = {c[1], pandoc.ColWidthDefault} end
  return t
end
