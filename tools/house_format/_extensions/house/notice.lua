-- The document's `notice` metadata, if any, set small in TeX Gyre Heros (the LaTeX route's \sffamily,
-- typeset-boxes.sty) and centred at the head of every page: in the brand's ink_second (an audience profile's,
-- through _brand.yml) where it has one, as the LaTeX route sets the stamp in typesetinksecond, and in grey
-- otherwise. Run at post-render, after Quarto's brand filter, so that the header comes
-- after the `brand-color` it declares. The value is Markdown, as the documents are; a caller that wants text printed
-- as typed backslash-escapes each ASCII punctuation mark (CommonMark 2.4). With no `notice`, the page has no header.
-- The notice's words are `house-notice`, none where there is no notice, which the header's house-cover sets in white.
function Meta(meta)
  if meta.notice == nil then
    quarto.doc.include_text("in-header", "#let house-notice = none")
    return nil
  end
  local value = meta.notice
  local blocks
  if pandoc.utils.type(value) == "Blocks" then
    blocks = value
  else
    blocks = pandoc.Blocks({pandoc.Plain(pandoc.Inlines(value))})
  end
  local content = pandoc.write(pandoc.Pandoc(blocks), "typst"):gsub("%s+$", "")
  quarto.doc.include_text("in-header", "#let house-notice = [" .. content .. "]\n"
    .. '#set page(header: align(center, text(font: "TeX Gyre Heros", size: 8pt, fill: brand-color.at("ink_second", default: luma(35%)), house-notice)))')
  return nil
end
