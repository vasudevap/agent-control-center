# Atlas GUI Design Principles

Working notes distilled from the alternate-GUI review pass on branch `codex/gui-alternate-second-opinion`. These describe patterns applied consistently once discovered, not a spec for new product behavior. Advisory reference only.

## 1. Mono/uppercase/tracked type is structural, never content

The small, uppercase, letter-spaced monospace treatment (`font-mono text-[11px] font-semibold uppercase tracking-[0.08em]`) marks a piece of UI as structural chrome: card titles, section headers, nav labels, eyebrows, legends, identifiers. It never appears on content values (names, dates, numbers, descriptions). If a field is user data rather than UI scaffolding, it gets a plain, readable font.

## 2. State is never color alone

Every status or risk indicator pairs an icon with its color. Color carries meaning faster, the icon makes that meaning legible to anyone who cannot rely on color, including at a glance in a crowded row. A label is added when there is room and dropped only where the icon and color pairing is already unambiguous and the layout is dense (tables, compact lists).

## 3. Icon-only indicators are bare and optically balanced

When a status or risk chip has no label, it drops its pill background and border. It becomes a bare glyph, not a shrunken badge. Each glyph is sized individually rather than uniformly, because different shapes read as different sizes at the same nominal dimension. Triangles (warning glyphs) read smaller than circles, diamonds, or check and x marks at equal pixel size, so they get a slightly larger box to look equivalent in weight next to the others.

## 4. Actionable cards look different from informational cards

A card whose rows lead somewhere (a detail page, a record) gets a shaded header (`bg-surface-secondary`, a bottom border) to signal that the body is interactive. A card that only displays information keeps a plain header. A card only earns the shaded treatment if every row inside it is genuinely and fully clickable. Partial interactivity (one link buried in a row of otherwise static text) does not qualify, and is a sign the row needs the stretched-link treatment described below before the card can be called actionable.

## 5. Stretched link for full-row clickability

Where a table row or list item should be entirely clickable rather than just its title, the row keeps exactly one real anchor. The row (or containing element) gets `relative`, and the anchor gets `relative z-10 after:absolute after:inset-0 after:content-['']`. This gives a full hit area without duplicating links or degrading accessibility, since there is still only one focusable element per row.

## 6. One font per row or column of values

Every value in a given row (or every value in a given column down a list) uses the same font treatment. Mixing a monospace date next to a plain-font name in the same row, or giving one field in a repeated list a different font than its neighbors, reads as an error rather than a design choice. This came up repeatedly: fleet roster timestamps, agent inventory fields, activity table timestamps, at-a-glance version strings all had to be normalized to match their neighbors.

## 7. Icon-bearing headers align to the title's line and edge

When a header has a leading icon next to a title, the icon sits on the title's baseline, not centered against a multi-line block. Anything below the title (eyebrow text above, description or meta text below) aligns its left edge to the title's text, not to the icon. The icon is a decoration on one line, not an anchor for the whole header block.

## 8. No redundant restatement

The same fact or figure should not appear twice on one page, or on a page and a persistent surface (status bar, sidebar) at the same time. Duplication reads as disagreement waiting to happen the moment the two copies drift out of sync, and it costs the user a second read for no new information. Cases fixed under this rule: the Overview metrics row repeating numbers already in the status bar, the Overview Fleet Roster repeating the Agents page, and Agent Detail's page header repeating the health and status fields already in the At-a-glance card.

## 9. Shared structural dimensions come from one variable

Measurements that multiple components must agree on, such as sidebar width or status bar height, are defined once as a CSS custom property and referenced everywhere, never independently re-guessed in each consuming component. This is what keeps the sidebar, status bar, and main content region from drifting out of alignment as any one of them changes.

## 10. Equivalent page types share structure

Pages that serve the same role in the product (for example, the two single-record detail pages: Agent Detail and Approval Detail) should share the same layout conventions unless there is a real reason to differ. The sticky-aside behavior on Approval Detail was the reference pattern Agent Detail was brought in line with, rather than each detail page evolving its own independent layout.

## 11. Interactive styling implies a real destination

A pill, chip, or badge that looks clickable (brand color, interactive-looking border or fill) should only be used where there is an actual interactive destination behind it. If there is nothing to click through to, the element should be styled as plain, static content (a neutral tag or label) so its appearance does not promise an affordance that does not exist.
