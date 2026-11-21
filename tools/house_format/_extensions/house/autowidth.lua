-- Every table's columns left to Typst (auto tracks), in place of pandoc's widths from the dashes of a pipe table's
-- separator line (pandoc manual, "Pipe tables"); the format's header then sizes a table that overflows the line by
-- tabulary's rule and leaves alone one given widths of its own. A document's `table-size` metadata, a share of its
-- body's size, sets its tables' type (the header's house-table-size; tools/typeset.py gives the summary 0.85).
function Table(t)
  for i, c in ipairs(t.colspecs) do t.colspecs[i] = {c[1], pandoc.ColWidthDefault} end
  return t
end

function Pandoc(doc)
  local share = doc.meta["table-size"] and tonumber(pandoc.utils.stringify(doc.meta["table-size"]))
  if share == nil then return nil end
  doc.blocks:insert(1, pandoc.RawBlock("typst", "#house-table-size.update(" .. share .. ")"))
  return doc
end
