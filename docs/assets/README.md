# docs/assets

| File | Role |
|---|---|
| `apex-oncology-architecture.svg` | **Source.** Hand-edited. The diagram itself. |
| `apex-oncology-architecture.png` | Render of the SVG, committed so `README.md` displays on GitHub. |

## Editing the architecture diagram

Edit the SVG, then re-render the PNG. Never edit the PNG — it has no other master, and a
correction made only to the PNG is lost the next time anyone re-renders.

The SVG is a plain coordinate grid with no transforms or nested groups, so labels are
greppable: find the text, change it, re-render.

### Re-rendering

Any SVG rasterizer works. Headless Chrome needs no install on a standard Windows image:

```powershell
$svg = (Resolve-Path docs/assets/apex-oncology-architecture.svg).Path
$out = (Resolve-Path docs/assets).Path + '\apex-oncology-architecture.png'
$chrome = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"

Start-Process -FilePath $chrome -Wait -NoNewWindow -ArgumentList @(
  '--headless=new', '--disable-gpu', '--hide-scrollbars',
  '--force-device-scale-factor=2',          # 2x for legibility on high-DPI screens
  '--window-size=1480,1080',                # must match the SVG width/height
  "--screenshot=$out",
  ('file:///' + ($svg -replace '\\','/'))
)
```

`--window-size` must match the SVG's `width` and `height` attributes, or the render is
cropped or padded. If you change the canvas size, change it in both places.

Equivalents, if you have them installed:

```
magick -density 192 -background white apex-oncology-architecture.svg apex-oncology-architecture.png
inkscape apex-oncology-architecture.svg -o apex-oncology-architecture.png -w 2960
rsvg-convert -w 2960 -b white apex-oncology-architecture.svg -o apex-oncology-architecture.png
```

## What to keep in step

The diagram repeats facts that live elsewhere. When those change, the diagram is stale
and nothing will tell you:

| Diagram element | Source of truth |
|---|---|
| AI Agents / MCP Clients row | `.mcp/context.yaml` → `entry_points.by_client` |
| AGENTS & MCP (Global) file list | repository root |
| Franchise boxes | `franchises/` |
| Context Chain panel | `AGENTS.md`, and `.mcp/context.yaml` → `context_chain` |
| How to Add a New Franchise steps | `templates/TEMPLATE_FRANCHISE.md` |

This repository previously carried a hand-made PNG with no source file. A `GEMINI.md`
entry point that never existed stayed visible in the README long after every text
reference to it was removed, because the label was pixels. That is the failure mode the
SVG source exists to prevent.
