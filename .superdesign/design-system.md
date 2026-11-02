# Lightning Voice Assistant — UI Design System

## Product and target

Native Windows desktop interview assistant. Keep the existing microphone capture, transcription, answer display, typed-question submission, clear action, and status feedback. Restyle the existing assistant window to match the supplied compact assistant-widget reference; do not turn it into a browser page or replace real controls with simulation controls.

## Visual direction

- Frameless Windows widget, exactly 480 × 434 px, with a 16 px rounded outer edge, thin cool-teal border, draggable header, and custom close control.
- Deep navy canvas `#0b1020`, dark surface `#111729`, raised surface `#151d31`, and fine blue-gray border `#26334a`.
- Bright aqua/teal `#56d6cf` is the primary accent, with pale teal `#8ce9e0` for emphasis.
- Soft white text `#edf4fa`; muted blue-gray `#8999ae`.
- Inter when installed, otherwise Segoe UI; compact status labels, bold question heading, and readable answer body.
- Main content stacks the detected question above the streamed answer in one compact column.
- Header has the lightning identity, concise current state, five-bar equalizer, rounded teal Listen control, and close control.
- The detected question and answer each sit in soft rounded cards with fine outlines.
- Footer keeps the pill-shaped clear action, configured local model, keyboard hints, status detail, and typed follow-up field with a pill-shaped answer action without making them the visual focus.
- Keep answer content scrollable without showing a scrollbar. Preserve high contrast and compact spacing; do not add unrelated navigation, promotional copy, sample interview content, or unsupported confidence scores.
- Listening state uses a restrained animated equalizer; keep it static while not recording.

## Target content and behavior

- Header: lightning mark, current state, rounded actual start/stop microphone control, equalizer, and close control.
- Question section: rounded detected/latest question card, capture timestamp, and whether it came from voice transcription or typed input.
- Answer section: rounded card; streamed answer remains scrollable by mouse wheel without a visible scrollbar.
- Footer: actual clear control, configured local model, keyboard hints, status details, and typed-question field.
- Primary microphone control must still start/stop actual audio capture. The existing clear action must remain available.
- The custom close control must call the app's normal shutdown path; dragging the header only moves the window.
- All controls must invoke real app behavior. Do not invent auto-listen, stealth, fullscreen, minimize, or simulation functionality if it does not exist in the source.
- Keep the typed entry responsive within the 480 px shell without clipping its submit control. Do not add a face/avatar; retain the lightning identity.

## Source palette reference

Adapted from the user-provided Figma widget's dark navy and aqua/teal palette. No global CSS file applies to this Tkinter application.
