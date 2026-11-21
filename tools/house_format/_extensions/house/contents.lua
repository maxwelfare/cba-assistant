-- The document's title as the PDF's Title, and its contents list, from its own headings, as on the LaTeX route
-- (typeset-common.sty, document.tex). The first level-1 heading, the title, is set as the document's title in its
-- words alone (an `{icon=...}` attribute is not part of them), by a rule at the body's start, where it is allowed even
-- when the title stands inside a float (columns.lua); Quarto's template has set it to none before the body.
-- Typst's outline of the level-2 and level-3 headings, under the heading Contents, stands before the first level-2
-- heading, after the title and dateline; each entry is a link to its heading with the heading's page number. Typst
-- makes the PDF's bookmarks from the headings itself, all but the title's (the header), as on the LaTeX route.
-- The list's title is a level-2 heading, set as the sections' are and outside the bookmarks; were it level 1, as by
-- default, the sections' bookmarks would leave the title's and stand beside it. Each entry is Typst's own (outline.entry)
-- with the page number in one box with the dot leader, so that the two stay on one line without the invisible word
-- joiner Typst puts between them, which a reader copying the line would get. A heading's icon (the header's
-- house-icon) is left out of its entry, as on the LaTeX route. A document whose `contents` metadata is false
-- (tools/typeset.py sets it for verse, as verse.tex sets no list, and for the executive summary, as summary.tex sets
-- none) gets no list.
local OUTLINE = [==[
#{
  show outline: set heading(level: 2)
  show <house-icon>: none
  show outline.entry: it => link(it.element.location(),
    it.indented(it.prefix(), [#it.body() #box(width: 1fr)[#box(width: 1fr, it.fill) #it.page()]]))
  outline(target: heading.where(level: 2).or(heading.where(level: 3)))
}]==]

function Pandoc(doc)
  local blocks = pandoc.Blocks({})
  local titled, listed = false, false
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 and not titled then
      local title = pandoc.utils.stringify(block.content):gsub('[\\"]', "\\%0")
      blocks:insert(1, pandoc.RawBlock("typst", '#set document(title: "' .. title .. '")'))
      titled = true
    elseif block.t == "Header" and block.level == 2 and not listed and doc.meta.contents ~= false then
      blocks:insert(pandoc.RawBlock("typst", OUTLINE))
      listed = true
    end
    blocks:insert(block)
  end
  doc.blocks = blocks
  return doc
end
