-- A span with an identifier, as the fill writes a reference-list entry (`[Its citation.]{#reference-2}`), is a link
-- target at its start, as on the LaTeX route (typeset-links.sty). Pandoc's Typst writer would put the label after the
-- span's last word and a zero-width space before its first, so a citation's link would land at the entry's end and
-- the text would hold a character nobody sees; the label goes instead on an empty metadata element before the words.
function Span(span)
  if span.identifier == "" then return nil end
  local target = pandoc.RawInline("typst", "#metadata(none)<" .. span.identifier .. ">")
  span.identifier = ""
  return pandoc.Inlines({target, span})
end
