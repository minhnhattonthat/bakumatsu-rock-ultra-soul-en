# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/PT_Serif-Web-Regular.ttf (licence: fonts/PT_Serif-OFL.txt) | ParaType PT Serif, Google Fonts (github.com/google/fonts, ofl/ptserif) | OFL 1.1 | yes, as rendered glyphs in font17.fnt | proportional ASCII in the game font (`tools/vwf.py`): ADV dialogue, back log, font17 menus | rendered at 12 px, 2 bpp, into the 17x17 KFNT cell; advances in header byte 0 |
| fonts/PT_Serif-Web-Bold.ttf (licence: fonts/PT_Serif-OFL.txt) | same family, Google Fonts (ofl/ptserif) | OFL 1.1 | yes, as rendered pixels in GIMs | chapter title cards (`tools/gfx.py` style `title`) | none |
| fonts/Anton-Regular.ttf (licence: fonts/anton-OFL.txt) | Google Fonts (github.com/google/fonts, ofl/anton) | OFL 1.1 | yes, as rendered pixels in GIMs | menu, label, notice and banner pictures (`gfx.py` styles `menu`, `small`, `notice`, `banner`) | none |
| fonts/Bangers-Regular.ttf (licence: fonts/bangers-OFL.txt) | Google Fonts (ofl/bangers) | OFL 1.1 | yes, as rendered pixels in GIMs | manga sound effects (`gfx.py` style `sfx`) | none |
| fonts/ArchivoBlack-Regular.ttf (licence: fonts/archivoblack-OFL.txt) | Google Fonts (ofl/archivoblack) | OFL 1.1 | yes, as rendered pixels in GIMs | tiny 32x16 labels (`gfx.py` style `plain`) | none |
