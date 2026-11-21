-- A verse document (its `verse` metadata; tools/typeset.py sets it for documents/verse/*.md) laid out as verse.tex
-- lays it out: its title centred and its title and headings in Lato bold; the body passed whole to the header's
-- house-verse as an array of items: each heading ("head"), table and image ("wide") across the page, and each run of
-- other blocks between them ("run") as an array of stanzas, each an array of lines: a paragraph of verse is a stanza
-- whose lines are those its hard line breaks end, a list a stanza of its lines (list_lines()), and any other block a
-- stanza of one line. Run at `pre-ast`, before Quarto makes images into figures.
local function wide(block)
  if block.t == "Header" or block.t == "Table" or block.t == "Figure" then return true end
  return (block.t == "Para" or block.t == "Plain") and #block.content == 1 and block.content[1].t == "Image"
end

local function line(inlines, before)
  local out = pandoc.Inlines({pandoc.RawInline("typst", "[" .. (before or ""))})
  out:extend(inlines)
  out:insert(pandoc.RawInline("typst", before and "]]," or "],"))
  return pandoc.Plain(out)
end

-- The lines of a paragraph, those its hard line breaks end, each with `before` (a list's indent and marker) or none.
local function para_lines(para, blocks, before)
  local words = pandoc.Inlines({})
  for _, inline in ipairs(para.content) do
    if inline.t == "LineBreak" then
      if #words > 0 then blocks:insert(line(words, before and before())) end
      words = pandoc.Inlines({})
    else
      words:insert(inline)
    end
  end
  if #words > 0 then blocks:insert(line(words, before and before())) end
end

local MARKS = {Period = "%d.", OneParen = "%d)", TwoParens = "(%d)", DefaultDelim = "%d."}

-- A list's lines, so that a list breaks across columns and pages between its lines as on the LaTeX route: each
-- paragraph of an item a line per hard line break, set by the header's house-list-line at the list's depth, the
-- item's first line with its marker; a list in an item one level deeper; any other block a line of its own.
local function list_lines(list, depth, blocks)
  for i, item in ipairs(list.content) do
    local mark = "•"
    if list.t == "OrderedList" then mark = (MARKS[list.delimiter] or "%d."):format(list.start + i - 1) end
    local first = true
    local function before()
      local marker = first and ('"' .. mark .. '"') or "none"
      first = false
      return "#house-list-line(" .. depth .. ", " .. marker .. ")["
    end
    for _, block in ipairs(item) do
      if block.t == "Para" or block.t == "Plain" then
        para_lines(block, blocks, before)
      elseif block.t == "BulletList" or (block.t == "OrderedList" and (block.style == "Decimal"
          or block.style == "DefaultStyle")) then
        first = false
        list_lines(block, depth + 1, blocks)
      else
        first = false
        blocks:extend({pandoc.RawBlock("typst", "["), block, pandoc.RawBlock("typst", "],")})
      end
    end
  end
end

local function stanza(block)
  local blocks = pandoc.Blocks({pandoc.RawBlock("typst", "(")})
  if block.t == "Para" then
    para_lines(block, blocks)
  elseif block.t == "BulletList" or (block.t == "OrderedList" and (block.style == "Decimal"
      or block.style == "DefaultStyle")) then
    list_lines(block, 0, blocks)
  else
    blocks:extend({pandoc.RawBlock("typst", "["), block, pandoc.RawBlock("typst", "],")})
  end
  blocks:insert(pandoc.RawBlock("typst", "),"))
  return blocks
end

function Pandoc(doc)
  if not doc.meta.verse then return nil end
  local blocks = pandoc.Blocks({pandoc.RawBlock("typst", "#show heading.where(level: 1): set align(center)\n"
    .. '#show heading: set text(font: "Lato", weight: "bold")'), pandoc.RawBlock("typst", "#house-verse((")})
  local open = false
  for _, block in ipairs(doc.blocks) do
    if wide(block) then
      if open then blocks:insert(pandoc.RawBlock("typst", ")),")) end
      open = false
      blocks:insert(pandoc.RawBlock("typst", '("' .. (block.t == "Header" and "head" or "wide") .. '", ['))
      blocks:insert(block)
      blocks:insert(pandoc.RawBlock("typst", "]),"))
    else
      if not open then blocks:insert(pandoc.RawBlock("typst", '("run", (')) end
      open = true
      blocks:extend(stanza(block))
    end
  end
  if open then blocks:insert(pandoc.RawBlock("typst", ")),")) end
  blocks:insert(pandoc.RawBlock("typst", "))"))
  doc.blocks = blocks
  return doc
end
