# CLAUDE.md — tallentin-vocabulary-engine

## Source of truth
- Single source of truth: Supabase `f31.build_tracker` (project `onzgonecbbpxwjhzqkqa`).
- At session open, read authority_pointer item `TALLENTIN_SCOPE` before doing anything else.

## Task scope
- Vocabulary tasks are `BT-V00`..`BT-V13`, `area='Vocabulary'`.
- One task per session. Do not mix tasks within a single session.

## Aim discipline
- Read [NOW.md](NOW.md) before any work in a session.
- If a request is off the aim stated in NOW.md, refuse and say exactly: "off-aim".

## File edits
- bak-then-write before every file edit: copy the file to a `.bak` backup before writing changes.
- Working file check: before touching `index.html`, grep it for `renderAnswerV2` first.

## Deprecated trackers
- `MASTER_TRACKER.md` and any `.xlsx` tracker are DEPRECATED (DEC-S149).
- Never read them as truth, even if present in the repo.
