-- The document's title as the PDF's Title, and its contents list, from its own headings (ported from the cost-benefit
-- project's house format). The first level-1 heading, the title, is set as the document's title in its words alone,
-- by a rule at the body's start; Quarto's template has set it to none before the body.
-- Typst's outline of the level-2 and level-3 headings, under the heading Contents, stands before the first level-2
-- heading; each entry is a link to its heading with the heading's page number. Typst makes the PDF's bookmarks from
-- the headings itself, all but the title's (the header).
-- The list's title is a level-2 heading, set as the sections' are and outside the bookmarks; were it level 1, as by
-- default, the sections' bookmarks would leave the title's and stand beside it. Each entry is Typst's own (outline.entry)
-- with the page number in one box with the dot leader, so that the two stay on one line without the invisible word
-- joiner Typst puts between them, which a reader copying the line would get. A document whose `contents` metadata is
-- false gets no list.
-- Where the metadata gives a `short-title` or a `kind` (summary, paper, appendix ...), the PDF's Title is the short
-- title (or else the title) and the kind, "Trans fat: summary", so that two documents of one case differ in a viewer's
-- tab, which shows the Title (tools/render.py sets DisplayDocTitle).
local OUTLINE = [==[
#{
  show outline: set heading(level: 2)
  show outline.entry: it => link(it.element.location(),
    it.indented(it.prefix(), [#it.body() #box(width: 1fr)[#box(width: 1fr, it.fill) #it.page()]]))
  outline(target: heading.where(level: 2).or(heading.where(level: 3)))
}]==]

local function quoted(text)
  return '"' .. text:gsub('[\\"]', "\\%0") .. '"'
end

function Pandoc(doc)
  local blocks = pandoc.Blocks({})
  local titled, listed = false, false
  local short = doc.meta["short-title"] and pandoc.utils.stringify(doc.meta["short-title"])
  local kind = doc.meta.kind and pandoc.utils.stringify(doc.meta.kind)
  local named = (short or kind) and (short or (doc.meta.title and pandoc.utils.stringify(doc.meta.title)))
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 and not titled then
      named = named or pandoc.utils.stringify(block.content)
      titled = true
    elseif block.t == "Header" and block.level == 2 and not listed and doc.meta.contents ~= false then
      blocks:insert(pandoc.RawBlock("typst", OUTLINE))
      listed = true
    end
    blocks:insert(block)
  end
  if named or kind then
    local title = named and kind and (named .. ": " .. kind) or named or kind
    blocks:insert(1, pandoc.RawBlock("typst", "#set document(title: " .. quoted(title) .. ")"))
  end
  doc.blocks = blocks
  return doc
end
