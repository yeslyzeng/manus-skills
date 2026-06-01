---
name: daily-assistant
description: Daily assistant workflows for any user. Handles morning calendar overviews, context-aware email triage (using sender relationship, company size, and prior history), evening meeting follow-up summaries, and topic-based to-do list maintenance. Use when setting up scheduled updates, generating daily summaries, or updating a user's action items.
---

# Daily Assistant

This skill enables a comprehensive daily assistant workflow. It integrates morning planning, context-aware email triage, evening follow-up extraction, and active to-do list maintenance using automated schedules.

---

## Setup: Connectors + User Identity

### Step 1: Enable Required Connectors

This skill requires three connectors. If the user hasn't set them up yet, prompt them to do so before proceeding:

| Connector | Purpose | How to enable |
| :--- | :--- | :--- |
| **Gmail** | Fetch unread emails, send Morning/Evening digests | Settings → Connectors → Gmail |
| **Google Calendar** | Fetch today's events and identify deep-work windows | Settings → Connectors → Google Calendar |
| **Slack** | Send Morning/Evening digests as Slack DMs | Settings → Connectors → Slack |

If a connector is missing, tell the user which one is needed and what it's used for, then pause until they confirm it's enabled.

### Step 2: Identify the User

Once connectors are active, determine:
1. **User's name** — used in greetings (e.g., "Hey Sarah,")
2. **User's email address** — used as the send-to address for emails, and to determine whether an email is addressed directly to the user (To: field) vs. CC'd only
3. **User's Slack user ID** — used as the `channel_id` for Slack DMs. Find it via `slack_read_user_profile` (defaults to current user) or `slack_search_users`.

Ask the user for these on first run if not already known. Store them for all subsequent runs.

---

## Delivery: Slack DM + Email

All Morning Digest and Evening Follow-up outputs MUST be delivered in this order:
1. **Slack DM** — send to the user's Slack user ID via `slack_send_message` (use the user ID as `channel_id`)
2. **Email** — send to the user's email address via `gmail` MCP (`gmail_send_messages`)
3. **In-chat** — display the same content in-chat

**Style rules (apply to both Slack and email):**
- Conversational, warm, easy to skim — like a message from a smart EA
- Very brief: 5–8 lines per section maximum, no walls of text
- No draft replies — just flag the action and move on
- Omit NOISE emails entirely — do not mention them, not even a count

**Slack-specific formatting rules** (see [references/slack-templates.md](references/slack-templates.md)):
- Use Slack markdown: `*bold*`, `_italic_`, `~strikethrough~`, `` `code` ``, `>blockquote`
- Section headers use bold + emoji on their own line (e.g. `*🎯 MOST IMPORTANT TASKS*`), not `━━━` dividers (those are email-only)
- Separate sections with a single blank line
- Keep each message under 5000 characters; split into 2 messages if needed
- Subject line equivalent: send as the first line of the Slack message in bold, e.g. `*🌅 Morning Digest — Wednesday, May 28*`

**Email-specific formatting rules** (see [references/email-templates.md](references/email-templates.md)):
- Subject line format: `🌅 Morning Digest — [Day, Date]` or `🌙 Evening Follow-up — [Day, Date]`
- Section dividers use `━━━ CENTERED HEADER ━━━` format
- No blank lines within sections

---

## Core Capabilities & Schedule Mapping

The Daily Assistant maintains a unified, persistent to-do list at `/home/ubuntu/todo.md` as its single source of truth.

| Time (Local) | Routine | Trigger Setup |
| :--- | :--- | :--- |
| **09:00 AM** | **Morning Digest** | `manus-config schedule create --title "Morning Digest" --cron "0 0 9 * * 1-5" --repeated --detail "Run the Morning Digest routine: fetch the user's calendar for today, triage unread emails using context-aware relationship scoring, update /home/ubuntu/todo.md, then send the brief Morning Digest email to the user's email address and show it in-chat."` |
| **06:00 PM** | **Evening Follow-up** | `manus-config schedule create --title "Evening Follow-up" --cron "0 0 18 * * 1-5" --repeated --detail "Run the Evening Follow-up routine: scan today's Granola meeting notes, extract action items, update /home/ubuntu/todo.md, then send the brief Evening Follow-up email to the user's email address and show it in-chat."` |
| **Ad-hoc** | **To-Do Maintenance** | Run ad-hoc as requested by the user. |

---

## Workflow A: Morning Digest (09:00 AM)

### Step 0: Reconcile todo.md
Before doing anything else, read `/home/ubuntu/todo.md` and check for any manually completed items (lines where the checkbox has been changed to `- [x]` since the last run).
- For each `- [x]` item found in the active sections (i.e., not already in the archive), archive it to `/home/ubuntu/todo_archive/todo_completed_YYYY_MM.md` and remove it from `todo.md`
- This ensures manual checkbox clicks in the Manus UI are always honoured before the digest runs

### Step 1: Fetch Calendar
Use `google-calendar` MCP to list today's events.
- Filter out all-day events unless "OOO" or "Travel"
- Identify deep-work windows (2+ uninterrupted hours)
- Note back-to-back conflicts

### Step 2: Triage Emails
Use `gmail` MCP to fetch unread emails. Apply rules from [references/calendar-email-rules.md](references/calendar-email-rules.md):
- Pre-screen: skip calendar notifications, access requests, automated alerts
- Score each email by context (prior history, company size, relationship)
- Apply the **Not Addressed to User** rule: if the user is CC'd only (not in To:), cap at FYI
- Apply the **Cold Email Demotion** rule: no prior relationship = NOISE or FYI at best
- Classify into: URGENT / ACTION / FYI only (omit NOISE entirely)
- For URGENT and ACTION items: note the suggested reply in-chat only, not in the email
- **Never expose triage reasoning in the output** — no context scores, no "addressed to X", no classification labels

### Step 3: Update To-Do List
Read `/home/ubuntu/todo.md`, add any urgent email action items, then re-sort using the topic-based schema in [references/todo-rules.md](references/todo-rules.md).

### Step 4: Compose and Send Morning Digest
1. Send Slack DM using [references/slack-templates.md](references/slack-templates.md) — Morning Digest section. Use the user's Slack user ID as `channel_id`.
2. Send email using [references/email-templates.md](references/email-templates.md) — Morning Digest section. Send to the user's email address via `gmail_send_messages`.
3. Display in-chat.

---

## Workflow B: Evening Follow-up (06:00 PM)

### Step 0: Reconcile todo.md
Before doing anything else, read `/home/ubuntu/todo.md` and check for any manually completed items (lines where the checkbox has been changed to `- [x]` since the last run).
- For each `- [x]` item found in the active sections, archive it to `/home/ubuntu/todo_archive/todo_completed_YYYY_MM.md` and remove it from `todo.md`
- This ensures manual checkbox clicks in the Manus UI are always honoured before new items are added

### Step 1: Scan Meeting Notes
Use `granola` MCP (`list_meetings` then `get_meetings`) to fetch notes for meetings held today.
- If no notes found, skip gracefully — do not prompt the user

### Step 2: Extract Action Items
Apply extraction logic from [references/meeting-followup.md](references/meeting-followup.md):
- Direct assignments to the user, implicit commitments, follow-up items
- Formulate each as a clear action verb + who + when

### Step 3: Update To-Do List
Append new items to `/home/ubuntu/todo.md` under the correct topic category.
Re-sort within each category by urgency (deadline-driven items first).

### Step 4: Compose and Send Evening Follow-up
1. Send Slack DM using [references/slack-templates.md](references/slack-templates.md) — Evening Follow-up section. Use the user's Slack user ID as `channel_id`.
2. Send email using [references/email-templates.md](references/email-templates.md) — Evening Follow-up section. Send to the user's email address via `gmail_send_messages`.
3. Display in-chat.

---

## Workflow C: To-Do List Maintenance (Ad-hoc)

The to-do list is maintained at `/home/ubuntu/todo.md` using the schema in [references/todo-rules.md](references/todo-rules.md).

**Always reconcile first:** Before any update, read `todo.md` and archive any `- [x]` items found in active sections. This handles manual checkbox clicks made between runs.

Update the list when:
- An urgent email action item surfaces during Morning Digest
- New action items are extracted during Evening Follow-up
- The user explicitly requests an update

---

## Related Resources

- **[references/calendar-email-rules.md](references/calendar-email-rules.md)** — Context-aware scoring matrix, cold email demotion rule, Not Addressed to User rule, and in-chat Morning Digest template.
- **[references/meeting-followup.md](references/meeting-followup.md)** — Meeting note scanning, action item extraction criteria, and in-chat Evening Follow-up template.
- **[references/todo-rules.md](references/todo-rules.md)** — Topic-based to-do schema, urgency sorting, 4D intake filter, and archiving rules.
- **[references/slack-templates.md](references/slack-templates.md)** — Slack DM templates for Morning Digest and Evening Follow-up, formatted for Slack markdown.
- **[references/email-templates.md](references/email-templates.md)** — Email templates for Morning Digest and Evening Follow-up sent to the user's email address.
