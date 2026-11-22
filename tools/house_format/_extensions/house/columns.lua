-- A document set in more than one column (its `columns` metadata; tools/typeset.py sets 2 for the executive summary)
-- opens with its head across the columns: the title, the paragraph straight after it unless it opens in bold or with an
-- image (the dateline, as tools/typeset.py's split_head() takes it), and a key-findings box straight after those,
-- placed at the top of the first page as one float in the page's scope (Typst's `place(top, scope: "parent",
-- float: true)`), with a rule 0.6 pt thick in the brand's `rule` colour under the title and dateline, as summary.tex
-- sets it; the rest flows in the columns below it. With the `balance` metadata, a number of lines, the rest is
-- set by the header's house-balance with that slack, so the columns end level. As summary.tex sets them: the columns
-- `gutter` apart (its columnsep); the title and the dateline each at the size and distance between baselines that
-- `head-title` and `head-dateline` give, as "19pt 22pt" (its \fontsize), the dateline in the brand's `ink_second`;
-- and the float 0.7 of a body line's pitch above the columns (its \textfloatsep). Run at `pre-ast`, before boxes.lua
-- turns the box into a callout.
local function meta(doc, key)
  local value = doc.meta[key]
  if value == nil then
    io.stderr:write("columns.lua: a document in columns needs the metadata `" .. key .. "`\n")
    os.exit(1)
  end
  return pandoc.utils.stringify(value)
end

-- The block `i` of `blocks` wrapped in the header's house-head-line at `sizes`, "19pt 22pt", in the colour `fill`
-- (a Typst colour, or none for the text's own); two blocks are added before the next.
local function head_line(blocks, i, sizes, fill)
  local size, pitch = sizes:match("^(%S+)%s+(%S+)$")
  blocks:insert(i + 1, pandoc.RawBlock("typst", "]"))
  blocks:insert(i, pandoc.RawBlock("typst", "#house-head-line(" .. size .. ", " .. pitch .. ", " .. fill .. ")["))
end

function Pandoc(doc)
  local columns = doc.meta.columns and tonumber(pandoc.utils.stringify(doc.meta.columns))
  if columns == nil or columns < 2 then return nil end
  local gutter, title, sizes = meta(doc, "gutter"), meta(doc, "head-title"), meta(doc, "head-dateline")
  local blocks = doc.blocks
  local first
  for i, block in ipairs(blocks) do
    if block.t == "Header" and block.level == 1 then first = i break end
  end
  if first == nil then return nil end
  local last = first
  local dateline = blocks[first + 1]
  if dateline and dateline.t == "Para" and dateline.content[1] and dateline.content[1].t ~= "Strong"
      and dateline.content[1].t ~= "Image" then
    last = first + 1
  end
  if last > first then
    head_line(blocks, last, sizes, 'brand-color.at("ink_second", default: rgb("#52514E"))')
    last = last + 2
  end
  head_line(blocks, first, title, "none")
  last = last + 2
  blocks:insert(last + 1, pandoc.RawBlock("typst", '#block(above: 4pt, below: 6pt, line(length: 100%, '
    .. 'stroke: 0.6pt + brand-color.at("rule", default: rgb("#E4E3DE"))))'))
  last = last + 1
  local box = blocks[last + 1]
  if box and box.t == "Div" and box.classes:includes("key-findings") then last = last + 1 end
  local slack = doc.meta.balance and tonumber(pandoc.utils.stringify(doc.meta.balance))
  if slack then
    blocks:insert(pandoc.RawBlock("typst", "]"))
    blocks:insert(last + 1, pandoc.RawBlock("typst", "#house-balance(" .. slack .. ")["))
  end
  blocks:insert(last + 1, pandoc.RawBlock("typst", "]"))
  blocks:insert(first, pandoc.RawBlock("typst", '#context place(top, scope: "parent", float: true, '
    .. 'clearance: 0.7 * (measure[x \\ x].height - measure[x].height))['))
  blocks:insert(1, pandoc.RawBlock("typst", "#set columns(gutter: " .. gutter .. ")"))
  return doc
end
