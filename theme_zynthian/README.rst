==============
Zynthian Theme
==============

Odoo 18 website / eCommerce theme replicating the look & feel of
https://zynthian.org (Grav CMS "hola" theme).

* Palette ``zynthian-1``: black ``#0D0A0B`` header/footer, dark red ``#862121`` accent,
  light grey ``#f1f1f1`` sections (alternative ``zynthian-2``).
* Fonts: only the ones imported by the zynthian.org Grav theme, bundled locally in
  ``static/src/fonts/grav`` (OFL, no Google Fonts): Inter (body, menu, buttons, h1/h6),
  Montserrat (headings), Space Grotesk (display titles, product names, home text
  blocks) and IBM Plex Mono (lead paragraphs).
* Square buttons, uppercase with wide letter-spacing, black -> red on hover.
* Header: logo on the left, menu aligned to the right (black bar). Menu entries
  pointing to ``/shop...`` or containing ``buy`` are shown as buttons. Search box,
  text, social links, call-to-action and "Sign in" are disabled (editable later).
* Shop (``/shop``), like shop.zynthian.org: categories as dark buttons on top, no
  sidebar / search / sort / filters / breadcrumb, 4 columns, cards with a white
  picture and a black bar with the name (Space Grotesk), price and cart button.
* Home content: "Text" blocks are always dark with large Space Grotesk Light text and
  Space Grotesk Bold headings, as the content migrated from the Odoo 16 shop expects.
* Footer legal links: /cookie-policy, /privacy-policy, /terms-conditions (as in
  shop.zynthian.org); smaller footer on mobile; "go top" button fixed bottom-right.
* Custom "Zynthian" footer (logo + social links + legal links), selectable in
  the editor (Footer > Template), plus "scroll to top" button.
* Snippet texts/images (cover, text-image, columns, picture, CTA) with Zynthian content.
* On install the website logo is set to the Zynthian logo (only if it is still Odoo's default).

Depends on ``theme_common`` (odoo/design-themes, branch 18.0) and ``website_sale``.
Install from Website > Configuration > Settings > Choose a theme.
