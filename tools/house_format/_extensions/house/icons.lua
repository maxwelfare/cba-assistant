-- A heading whose attributes carry `icon-glyph=CODE` (tools/typeset.py's heading_icons() writes it beside the
-- heading's `icon=NAME`, CODE the Tabler glyph's code point in hexadecimal) gets the header's house-icon before its
-- words. Run after Quarto's own filters, on text whose cross-references the shared renderer resolved from the
-- heading's words, so that a reference to the heading prints its number or its words alone.
function Header(h)
  local code = h.attributes["icon-glyph"]
  if code == nil then return nil end
  h.content:insert(1, pandoc.RawInline("typst", '#house-icon("\\u{' .. code .. '}")'))
  return h
end
