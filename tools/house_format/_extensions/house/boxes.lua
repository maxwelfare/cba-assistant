-- The documents' boxes as Quarto callouts. `::: key-findings` becomes a tip, `::: callout` a warning and
-- `::: worked-example` a note, each titled by its first bold words less a final period; `::: credit` is no box, its
-- words small and grey as the notice's, or in an audience edition's `ink_second`. Each box stands in a content block in
-- which `callout` is the header's house-callout with the box's kind and the brand's colours, so an audience edition's
-- colours reach it (the header). A Div with no class passes untouched. Any other class, or a titled kind whose
-- first block does not open in bold, stops the render with a line on stderr. Run at `pre-ast`, before Quarto reads
-- callouts; it uses pandoc's API alone, so `pandoc -L` runs it too.
local CALLOUT = {["key-findings"] = "callout-tip", callout = "callout-warning", ["worked-example"] = "callout-note"}

local function refuse(message)
  io.stderr:write("boxes.lua: " .. message .. "\n")
  os.exit(1)
end

function Div(div)
  if #div.classes == 0 then return nil end
  for _, class in ipairs(div.classes) do
    if CALLOUT[class] == nil and class ~= "credit" then
      refuse("no box `" .. class .. "`: the boxes are key-findings, callout, worked-example and credit")
    end
  end
  local kind = div.classes[1]
  if kind == "credit" then
    local blocks = pandoc.Blocks({pandoc.RawBlock("typst",
      '#block[#set text(size: 8pt, fill: brand-color.at("ink_second", default: rgb("#52514E")))')})
    blocks:extend(div.content)
    blocks:insert(pandoc.RawBlock("typst", "]"))
    return blocks
  end
  local first = div.content[1]
  if first == nil or first.t ~= "Para" or #first.content == 0 or first.content[1].t ~= "Strong" then
    local words = first and pandoc.utils.stringify(first) or ""
    refuse("a `" .. kind .. "` box opens with its title in bold: " .. words:sub(1, 60))
  end
  local title = first.content[1].content:clone()
  local last = title[#title]
  if last and last.t == "Str" and last.text:sub(-1) == "." then
    last.text = last.text:sub(1, -2)
    if last.text == "" then title:remove(#title) end
  end
  local rest = first.content:clone()
  rest:remove(1)
  while #rest > 0 and (rest[1].t == "Space" or rest[1].t == "SoftBreak" or rest[1].t == "LineBreak") do
    rest:remove(1)
  end
  local blocks = div.content:clone()
  if #rest > 0 then blocks[1] = pandoc.Para(rest) else blocks:remove(1) end
  blocks:insert(1, pandoc.Header(2, title))
  return pandoc.Blocks({
    pandoc.RawBlock("typst", '#[#let callout = house-callout.with("' .. kind .. '", brand-color)'),
    pandoc.Div(blocks, pandoc.Attr(div.identifier, {CALLOUT[kind]}, div.attributes)),
    pandoc.RawBlock("typst", "]"),
  })
end
