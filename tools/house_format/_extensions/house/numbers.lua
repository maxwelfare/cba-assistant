-- A table column whose body cells are all numbers is right-aligned, whatever the pipe table's separator line says
-- ("Tables use few rules and right-aligned numbers", research/layout_and_graph_packages.md 2.3 in tag
-- archive-2026-11-14). A number is an optional sign (+, - or the minus sign), an optional $, £ or €, digits with
-- optional thousands commas and an optional decimal part, and an optional %. Every other column keeps its alignment.
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

function Table(t)
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
