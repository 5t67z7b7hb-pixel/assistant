# Theme

## Existing UI tokens

The current UI is a split-pane Tkinter screen styled with values declared in `LightningStealthAssistant.setup_ui` (`main.py:387-413`).

| Token | Value |
|---|---|
| background | `#0a0805` |
| panel | `#15110b` |
| panel_light | `#1a130b` |
| input | `#100d08` |
| text | `#f3e6d0` |
| muted | `#9c8a6c` |
| accent | `#ff7a00` |
| accent2 | `#ffc83d` |
| border | `#3a2e1d` |
| success | `#ffc83d` |
| warning | `#9c8a6c` |
| danger | `#ff7a00` |
| stop | `#ffc83d` |
| stop_text | `#1a0d00` |

Typography uses Inter where installed and otherwise Segoe UI, at 7-14 px. Layout spacing is set with Tkinter pack/grid padding; there is no CSS, Tailwind configuration, theme provider, or separate token file.
