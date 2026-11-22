-- A table column whose body cells are all numbers is right-aligned, whatever the pipe table's separator line says
-- ("Tables use few rules and right-aligned numbers", research/layout_and_graph_packages.md 2.3 in tag
-- archive-2026-11-14). A number is an optional sign (+, - or the minus sign), an optional $, £ or €, digits with
-- optional thousands commas and an optional decimal part, and an optional %. Every other column keeps its alignment.
-- A body cell outside a table's first column that holds a letter (A to Z) and is no number is prose: each is written
-- to stderr as a line "doc-warning: ...", which tools/render.py lists in its report's warnings, since a table's body
-- holds numbers and its text goes in the first column or a footnote (the owner, 2026-11-21: "The table shoudl just be
-- nymbers, any text goes in the left column or a footntote. this should be a general rule"; a warning rather than a
-- refusal, and the letter as the mark of prose, are the seat's).
local function is_number(text)
  local s = text:gsub("^%s+", ""):gsub("%s+$", "")
  s = s:gsub("^[+-]", "", 1):gsub("^\u{2212}", "", 1)
  s = s:gsub("^[$]", "", 1):gsub("^\u{00A3}", "", 1):gsub("^\u{20AC}", "", 1)
  s = s:gsub("%%$", "", 1)
  local whole, decimals = s:match("^([%d,]+)(.*)$")
  if whole == nil or not (decimals == "" or decimals:match("^%.%d+$")) then return false end
  if not whole:find(",") then return whole:match("^%d+$") ~= nil end
  local first, rest = whole:match("^(%d%d?%d?)(,.*)$")
  return first ~= nil and rest:gsub(",%d%d%d", "") == ""
end

local tables = 0

local function name(t)
  local caption = pandoc.utils.stringify(t.caption.long)
  if caption ~= "" then return '"' .. caption .. '"' end
  local head = t.head.rows[1]
  local first = head and head.cells[1] and pandoc.utils.stringify(head.cells[1].contents) or ""
  return "number " .. tables .. ' (headed "' .. first .. '")'
end

local function column(t, i)
  local head = t.head.rows[#t.head.rows]
  local cell = head and head.cells[i]
  return cell and pandoc.utils.stringify(cell.contents) or tostring(i)
end

function Table(t)
  tables = tables + 1
  for _, body in ipairs(t.bodies) do
    for _, row in ipairs(body.body) do
      for i, cell in ipairs(row.cells) do
        local text = pandoc.utils.stringify(cell.contents)
        if i > 1 and text:find("%a") and not is_number(text) then
          io.stderr:write("doc-warning: table " .. name(t) .. ', column "' .. column(t, i) .. '" holds prose in a '
            .. 'body cell, "' .. text .. '"; a table\'s body holds numbers, and its text goes in the first column '
            .. "or a footnote\n")
        end
      end
    end
  end
  for i, spec in ipairs(t.colspecs) do
    local cells = 0
    local numbers = true
    for _, body in ipairs(t.bodies) do
      for _, row in ipairs(body.body) do
        local cell = row.cells[i]
        if cell ~= nil then
          cells = cells + 1
          numbers = numbers and is_number(pandoc.utils.stringify(cell.contents))
        end
      end
    end
    if numbers and cells > 0 then t.colspecs[i] = {pandoc.AlignRight, spec[2]} end
  end
  return t
end
