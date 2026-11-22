// The house format's Typst: the case layer over the shared base format (shared tools/render_format/_extensions/doc,
// which sets the tables, links, contents, number columns, equations and figure numbering). tools/typeset.py renders
// with the shared renderer (shared tools/render.py, format doc-typst) and names this file in the metadata's
// include-in-header, after the base format's header, and the filters beside it (columns.lua, boxes.lua, verse.lua
// before Quarto reads the document, notice.lua at post-render).
// A heading's icon is left out of the contents list (house-icon, below), as the LaTeX route's entries held the
// heading's words alone.
#show outline: it => { show <house-icon>: none; it }
// No character hangs past the line's end (Typst's overhang, its default), since that sets a comma or a hyphen past the
// right margin, which the shared renderer refuses; the LaTeX route had microtype's protrusion off for the same
// reason (typeset-common.sty, notes/pdf_layout_review.md 3.3).
#set text(overhang: false)
// The summary's two columns end level, as summary.tex's flushend ends them (the plan's risk 3). The body below
// the head (columns.lua wraps it in house-balance when the `balance` metadata is given) is set in columns as
// short as hold it: the least height at which it fits two columns of its width is found by bisection, a body
// that does not fit filling the height it is measured in, and a float of empty space across both columns at
// the page's foot shortens them to that height and `slack` lines more. tools/typeset.py renders with more slack
// where the page then overruns. The column's foot is found by a mark placed at its bottom, so the page's
// margins need not be known here.
#let house-balance(slack, body) = {
  place(bottom)[#metadata(none)<house-column-foot>]
  layout(region => context {
    let room = locate(<house-column-foot>).position().y - here().position().y
    let height(it) = measure(block(width: region.width, it)).height
    let fits(column) = measure(columns(2, gutter: 1em, body), width: 2 * region.width + 1em,
      height: column).height < column
    let (low, high) = (0pt, height(body) + 1pt)
    for _ in range(20) {
      let middle = (low + high) / 2
      if fits(middle) { high = middle } else { low = middle }
    }
    let column = high + slack * (height[x \ x] - height[x])
    if column < room { place(bottom, scope: "parent", float: true, clearance: 0pt, block(height: room - column)) }
    body
  })
}
// An audience edition's colours (step 7): tools/typeset.py writes the profile's colours as the palette of the
// document's brand (its front matter), by the role names of typeset-boxes.sty, and Quarto gives them as `brand-color`. Each
// box takes its rule and icon colour and its title band's ground from its roles, as the LaTeX route's boxes do
// (key-findings: accent on panel; callout: accent_caveat on caveat_ground; worked-example: neutral on panel),
// and its text is the profile's ink; a role the profile leaves out keeps Quarto's colour for that callout kind.
// boxes.lua binds `callout` to this function, with its box's kind and the brand's colours, around each box.
#let house-roles = ("key-findings": ("accent", "panel"), callout: ("accent_caveat", "caveat_ground"),
  "worked-example": ("neutral", "panel"))
// When the Quarto pin moves (shared tools/render_format/quarto.toml), recheck house-callout: it is a copy of
// Quarto 1.11.9's `callout` (share/formats/typst/pandoc/quarto/definitions.typ, line 163, in the 1.11.9 tree), with its
// insets and colours changed.
// The box is drawn as Quarto 1.11.9's template draws `callout`, in the same nested blocks (which Quarto's figure
// rule for a cross-referenced callout takes apart), but with typeset-boxes.sty's 4 pt above and below the title
// and the body where Quarto has 8 pt, so that a box is about as deep as on the LaTeX route.
#let house-callout(kind, colours, body: [], title: "Callout", background_color: rgb("#dddddd"), icon: none,
    icon_color: black, body_background_color: white) = {
  let (rule, ground) = house-roles.at(kind)
  if rule in colours { icon_color = colours.at(rule) }
  if ground in colours { background_color = colours.at(ground) }
  set text(fill: colours.ink) if "ink" in colours
  let inset = (x: 8pt, y: 4pt)
  block(breakable: false, fill: background_color, stroke: (paint: icon_color, thickness: 0.5pt, cap: "round"),
    width: 100%, radius: 2pt,
    block(inset: 1pt, width: 100%, below: 0pt, block(fill: background_color, width: 100%,
      inset: inset)[#if icon != none [#text(icon_color, weight: 900)[#icon] ]#title]) +
    if body != [] {
      block(inset: 1pt, width: 100%, block(fill: body_background_color, width: 100%, inset: inset, body))
    })
}
// The one-page summary's head (columns.lua): `body`, its title or its dateline, at `size` with its lines'
// baselines `pitch` apart, as summary.tex's \fontsize{size}{pitch} sets them, in `fill` (none: the text's own).
// Typst's leading runs from a line's baseline to the next line's top edge, the face's cap height, so it is the
// pitch less the cap height measured in the face the line is set in (the title's own in a heading).
#let house-head-line(size, pitch, fill, body) = {
  set text(size: size)
  set text(fill: fill) if fill != none
  show heading: set text(size: size)
  show heading: it => context { set par(leading: pitch - measure[X].height); it }
  context { set par(leading: pitch - measure[X].height); body }
}
// The policy paper's cover, a page of its own, as document.tex's \typesetcover sets it (layout migration step 9):
// a band of the accent colour 0.5 in deep across the top of the page, the page notice in white on it with its
// baseline 0.3 in from the top (typeset-boxes.sty); 1.1 in down the text block the title's icon, a character of
// the stored Tabler font, at 64 pt in the accent colour and 20 pt above the title; the title at 30 pt in the
// black weight in the ink, 16 pt above the dateline at 13 pt in ink_second, all in `family` (Lato, or an
// audience profile's heading font, as theme_tex() replaces Lato there); `foot`, the credit, at the page's foot.
// No page number. `colours` is the brand's palette, `icon` the glyph or none, `notice` the page notice
// (notice.lua's house-notice) or none. The lines stand where TeX puts them: each line's baseline is its
// \baselineskip below the end of what is above it (64 pt for the icon, 36 pt for the title's lines, 18 pt for
// the dateline's), after \topskip (11 pt) and the \parskip of 9 pt (half the 18 pt \baselineskip) before each
// paragraph; each line is therefore set with no height above or below its baseline, its leading the
// \baselineskip, and the space before it written out.
#let house-cover(colours, family, icon, notice, body, foot) = page(numbering: none, header: none,
  background: {
    place(top, rect(width: 100%, height: 0.5in, fill: colours.at("accent", default: rgb("#2A78D6"))))
    if notice != none {
      place(top + center, dy: 0.3in, text(font: "TeX Gyre Heros", size: 8pt, fill: white, top-edge: "baseline", bottom-edge: "baseline", notice))
    }
  }, {
    set text(font: family, size: 13pt, fill: colours.at("ink_second", default: rgb("#52514E")))
    set par(justify: false)
    {
      set text(top-edge: "baseline", bottom-edge: "baseline")
      set par(leading: 18pt, spacing: 9pt + 18pt)
      show heading.where(level: 1): set text(font: family, size: 30pt, weight: "black",
        fill: colours.at("ink", default: rgb("#0B0B0B")))
      show heading.where(level: 1): set par(leading: 36pt)
      show heading.where(level: 1): set block(above: 0pt, below: 16pt + 9pt + 18pt)
      v(1.1in + 11pt + 9pt)
      if icon != none {
        v(64pt)
        block(above: 0pt, below: 0pt, text(font: "tabler-icons", size: 64pt,
          fill: colours.at("accent", default: rgb("#2A78D6")), icon))
        v(20pt + 9pt)
      }
      v(36pt)
      body
    }
    v(1fr)
    foot
  })
// A heading's `{icon=NAME}` (tools/typeset.py writes the call, with the Tabler glyph): the icon in the heading's
// size and colour, 0.4 em before its words, as typeset-common.sty's \typesetheadicon sets it; labelled so that the
// contents list leaves it out (contents.lua), as the LaTeX route's entries hold the heading's words alone; drawn
// in a context, so that the bookmark's text, which Typst takes from the heading's words, holds no icon either.
#let house-icon(glyph) = [#box(context text(font: "tabler-icons", glyph) + h(0.4em))<house-icon>]
// The verse layout, as verse.tex sets it (layout migration step 9). verse.lua passes the body of a verse
// document to house-verse whole, as an array of items in order: ("head", a heading), ("wide", a table or an
// image) and ("run", the stanzas of a run of verse between them, each an array of lines). The verse is set in
// two columns 0.3 in apart, each line a paragraph of its own that hangs 1.5 em when it wraps, the lines of a
// stanza a line apart and stanzas a paragraph's space apart. As multicols fills every page's two columns and
// balances only the last page of each run, house-verse lays the body out page by page itself, measuring
// each piece: a heading or a wide item goes on the page if it fits, a heading only where seven lines' room is
// left (verse.tex's needspace) and with the wide item after it; a run fills two columns of the room left on
// each page, the lines that fit found by bisection on the line count, until its remaining lines fit the
// page's room; those are set in columns as short as hold them (the least height, again by bisection), and
// the next item follows below. Each page ends with a column break, so the pages fall where the measures put
// them. The layout depends only on where the body starts, which is read from the previous layout, and not on
// where its lines fell before, so every run's split follows from those above it in one layout. A wide item
// taller than a page (a long table) is set as it comes, breaking across pages, and the items after it are
// laid out by a new call, which reads where it ends. The foot of the text block, from which the room left is
// read, is marked once, at the bottom of the first page, since a mark placed inside the layout would stand at
// the foot of the layout's own block. Columns that overflow measure as tall as the height
// given, give or take a rounding error of the order of 1e-12 pt, so lines fit only where they measure at
// least 0.01 pt shorter (a margin of this route's, far above the rounding and far below anything seen on
// the page); a page's columns are 0.02 pt shorter than its room for the same reason.
#let house-trim(c) = {
  if c.func() != [].func() { return c }
  let kids = c.children
  while kids.len() > 0 and (kids.first() == [ ] or kids.first().func() == parbreak) { kids = kids.slice(1) }
  while kids.len() > 0 and (kids.last() == [ ] or kids.last().func() == parbreak) { kids = kids.slice(0, -1) }
  kids.join()
}
// A line of a list in verse (verse.lua's list_lines()): indented 1.5 em a level, its marker, on the item's first
// line, set in the 1.5 em before it (an indent and marker width of this route's).
#let house-list-line(depth, marker, body) = pad(left: (depth + 1) * 1.5em, {
  if marker != none { h(-1.5em); box(width: 1.5em, marker) }
  body
})
#let house-verse(items, nested: false) = {
  if not nested { place(bottom)[#metadata(none)<house-verse-foot>] }
  layout(region => context {
    let foot = query(<house-verse-foot>)
    let full = region.height
    let cap = if foot.len() == 0 { full } else { foot.first().location().position().y - here().position().y }
    let leading = par.leading
    let verse(part) = {
      set par(hanging-indent: 1.5em)
      let groups = ()
      for (s, line) in part {
        if groups.len() > 0 and groups.at(-1).at(0) == s { groups.at(-1).at(1).push(line) } else { groups.push((s, (line,))) }
      }
      for (_, stanza) in groups { block({ set par(spacing: leading); stanza.join(parbreak()) }) }
    }
    let wide(part) = columns(2, gutter: 0.3in, verse(part))
    let height(parts) = measure(block(width: region.width, parts.join())).height
    let fits(part, column) = measure(wide(part), width: region.width, height: column).height < column - 0.01pt
    let least(part) = {
      let (low, high) = (0pt, measure(block(width: (region.width - 0.3in) / 2, verse(part))).height + 1pt)
      for _ in range(20) {
        let middle = (low + high) / 2
        if fits(part, middle) { high = middle } else { low = middle }
      }
      high
    }
    // The most lines from the start of `part` that fit two columns `column` high.
    let fill(part, column) = {
      let (low, high) = (0, part.len())
      while low < high {
        let middle = calc.quo(low + high + 1, 2)
        if fits(part.slice(0, middle), column) { low = middle } else { high = middle - 1 }
      }
      low
    }
    let step = height((verse(((0, [x]), (0, [x]))),)) - height((verse(((0, [x]),)),))
    // `page`: the pieces set so far on the current page; `top`: whether nothing is above them on it.
    let (out, page, top, rest) = ((), (), cap >= full - 0.01pt, none)
    for (i, (kind, item)) in items.enumerate() {
      if kind == "run" {
        let lines = ()
        for (s, stanza) in item.enumerate() {
          for line in stanza { lines.push((s, house-trim(line))) }
        }
        while true {
          let column = cap - height(page + (block(height: 0pt),)) - 0.02pt
          if fits(lines, column) {
            let piece = block(height: least(lines), breakable: false, wide(lines))
            out.push(piece)
            page.push(piece)
            break
          }
          let end = fill(lines, column)
          if end == 0 and not (top and page.len() == 0) {
            out.push(colbreak(weak: page.len() > 0))
            (page, cap, top) = ((), full, true)
            continue
          }
          end = calc.max(end, 1)  // a line taller than a page is set on its own page
          out.push(block(height: column, breakable: false, wide(lines.slice(0, end))))
          out.push(colbreak(weak: true))
          (page, cap, top) = ((), full, true)
          lines = lines.slice(end)
        }
      } else if height((item,)) > full {
        out.push(item)
        rest = items.slice(i + 1)
        break
      } else {
        let need = (item,)
        if kind == "head" and i + 1 < items.len() and items.at(i + 1).at(0) != "run" {
          if height((items.at(i + 1).at(1),)) <= full { need.push(items.at(i + 1).at(1)) }
        }
        let short = kind == "head" and cap - height(page) < 7 * step
        if not (top and page.len() == 0) and (short or height(page + need) > cap - 0.01pt) {
          out.push(colbreak(weak: page.len() > 0))
          (page, cap, top) = ((), full, true)
        }
        out.push(item)
        page.push(item)
      }
    }
    out.join()
    if rest != none and rest.len() > 0 { house-verse(rest, nested: true) }
  })
}
