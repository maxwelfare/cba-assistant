-- A table cell whose text opens with Typst markup ("/ " a term, "- " or "+ " a list item, "= " a heading, "1. " a
-- numbered item: the marker alone, then a space or nothing) prints as written. Pandoc's Typst writer puts a cell's
-- text at the start of a content block, where Typst reads such an opening as markup ("/ per year" stops the build
-- with "expected colon"), so the marker is escaped with a backslash. Run last, so the other filters read the cell's
-- text as written.
local function escape(cell)
  local block = cell.contents[1]
  if block == nil or (block.t ~= "Plain" and block.t ~= "Para") then return end
  local first, after = block.content[1], block.content[2]
  if first == nil or first.t ~= "Str" or not (after == nil or after.t == "Space") then return end
  local text = first.text
  if text:match("^[-+/]$") or text:match("^=+$") then
    block.content[1] = pandoc.RawInline("typst", "\\" .. text:sub(1, 1))
    if #text > 1 then table.insert(block.content, 2, pandoc.Str(text:sub(2))) end
  elseif text:match("^%d+%.$") then
    block.content[1] = pandoc.RawInline("typst", text:sub(1, -2) .. "\\.")
  end
end

function Table(t)
  for _, row in ipairs(t.head.rows) do for _, cell in ipairs(row.cells) do escape(cell) end end
  for _, body in ipairs(t.bodies) do
    for _, row in ipairs(body.head) do for _, cell in ipairs(row.cells) do escape(cell) end end
    for _, row in ipairs(body.body) do for _, cell in ipairs(row.cells) do escape(cell) end end
  end
  for _, row in ipairs(t.foot.rows) do for _, cell in ipairs(row.cells) do escape(cell) end end
  return t
end
