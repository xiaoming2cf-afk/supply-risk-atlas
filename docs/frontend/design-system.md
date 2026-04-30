# Frontend Design System

The first frontend surface is an operational dashboard, not a marketing page.

## Visual Direction

- Dark industrial command-center UI.
- World map and network as the first visual signal.
- Risk expressed through heat, path color, and confidence.
- Dense but readable operational layout.
- No nested cards.
- No notebook-only or screenshot-only UI.

## Required States

Each production page must support:

- loading
- empty
- error
- stale version
- partial data

## Version Visibility

Every prediction, explanation, simulation, and report UI must surface graph, feature, label, model, and `as_of_time` metadata.
