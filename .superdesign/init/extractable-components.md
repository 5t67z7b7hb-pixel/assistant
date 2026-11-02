# Extractable UI Components

The app does not currently define reusable UI components in separate source files. The following visual patterns are embedded in `main.py` and could be separated if future screens need them.

## Layout Components

### AssistantWindow
- Source: `main.py:387-706`
- Category: layout
- Description: Frameless split-pane assistant with live status/equalizer, detected question, answer surface, footer controls, and typed-question entry.
- Extractable props: status, listening state, current question and answer, submit and clear callbacks.
- Hardcoded: Current labels, hotkey help, widget structure, fonts, and colors.

## Basic Components

### ListeningControls
- Source: `main.py:539-566`
- Category: basic
- Description: Start/stop listening and clear actions with keyboard shortcut help.
- Extractable props: recording state, status, start/stop callback, clear callback.
- Hardcoded: Button labels, shortcut text, colors, and layout.

### AnswerPanel
- Source: `main.py:502-533`
- Category: basic
- Description: Scrollable transcript and answer surface with styled headings and question text.
- Extractable props: rendered question and answer content.
- Hardcoded: Section labels, typography, colors, and spacing.

### AskQuestionField
- Source: `main.py:571-602`
- Category: basic
- Description: Typed-question entry with placeholder, Enter submission, and answer action.
- Extractable props: placeholder, submit callback, entry value.
- Hardcoded: Label, placeholder text, button label, colors, and spacing.

### ListeningEqualizer
- Source: `main.py:450-451, 606-627`
- Category: basic
- Description: Five-bar activity indicator animated while audio capture is active.
- Extractable props: listening state.
- Hardcoded: Bar count, animation patterns, colors, and dimensions.

### DetectedQuestion
- Source: `main.py:467-500, 655-672`
- Category: basic
- Description: Left-pane question display with detection time and voice-versus-typed source.
- Extractable props: question, timestamp, source.
- Hardcoded: Badge labels, typography, colors, and spacing.
