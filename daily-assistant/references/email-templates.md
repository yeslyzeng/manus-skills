# Email Templates for Daily Assistant

These are the brief, conversational email templates used when sending the Morning Digest and Evening Follow-up to the user's email address. Keep emails skimmable — a busy person should be able to read the whole thing in under 60 seconds.

---

## Morning Digest Email

**Subject:** `🌅 Morning Digest — [Weekday, Month DD]`

**Style:** Warm, direct, no fluff. Lead with the Most Important Tasks, then calendar, then emails. No draft replies. No NOISE section.

**Template:**

```
Subject: 🌅 Morning Digest — Wednesday, May 27

Hey [User Name],

Here's your morning rundown.

━━━━━━━━━━━━━━━ MOST IMPORTANT TASKS ━━━━━━━━━━━━━━━

1. [Task] — [one-line reason why it's #1]
2. [Task] — [one-line reason]
3. [Task] — [one-line reason]

━━━━━━━━━━━━━━━━━━━━ CALENDAR ━━━━━━━━━━━━━━━━━━━━━

[Time]   [Event] — [location if relevant]
[Time]   [Event]
Deep work window: [time block]

━━━━━━━━━━━━━━━━━━━━ EMAILS ━━━━━━━━━━━━━━━━━━━━━━━

🚨 URGENT
[Sender] — [Company]
"[Subject]"
[1 sentence: what they need + why it matters]
→ [Gmail thread URL]

📋 ACTION
[Sender] — [Company]
"[Subject]"
[1 sentence: what they need]
→ [Gmail thread URL]

💬 FYI
• [Sender] — [1-line summary].
• [Sender] — [1-line summary].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have a great day!
```

**Formatting rules:**
- Section dividers use `━` characters with the section title **centered** inside them, e.g.: `━━━━━━━━━━━━━━━ MOST IMPORTANT TASKS ━━━━━━━━━━━━━━━`
- **No blank lines within a section** — items run flush against each other with no empty lines between them
- **One blank line before and after each divider line** — this is the only vertical spacing in the email
- Most Important Tasks: numbered list, one per line, no blank lines between items
- Calendar: one line per event, no blank lines between events
- Emails: URGENT and ACTION items are compact blocks (sender, company, subject, summary, link — no blank lines between these lines); FYI items are a tight bulleted list
- Omit NOISE entirely — do not mention archived emails
- If there are no URGENT or ACTION emails, skip those sections entirely and just show FYI
- Include Gmail deep links as plain-text `→ URL` on the line after each email item
- **Never expose triage reasoning** — no context scores, no "addressed to X", no classification labels

---

## Evening Follow-up Email

**Subject:** `🌙 Evening Follow-up — [Weekday, Month DD]`

**Style:** Warm wrap-up. Lead with what was added from meetings, then show the full updated to-do list organized by topic.

**Template:**

```
Subject: 🌙 Evening Follow-up — Wednesday, May 27

Hey [User Name],

Here's what came out of today's meetings, plus your updated to-do list.

━━━━━━━━━━━━━━━━━━ NEW ACTION ITEMS ━━━━━━━━━━━━━━━━━

From [Meeting Name]:
→ https://app.granola.ai/meetings/{meetingId}
• [Action item] — [brief context, deadline if any]
• [Action item]

From [Meeting Name]:
→ https://app.granola.ai/meetings/{meetingId}
• [Action item]

(If no meetings had notes: "No meeting notes found today — nothing new to add.")

━━━━━━━━━━━━━━━━━━━ YOUR TO-DO LIST ━━━━━━━━━━━━━━━━━

[Paste the full /home/ubuntu/todo.md content here, formatted as plain text]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

See you tomorrow!
```

**Rules:**
- New action items: grouped by source meeting, one bullet per item, max one line each; include a Granola deep link per meeting as a plain-text `→ URL` on the line after the meeting name
- Full to-do list: always included, organized by topic category (see todo-rules.md) — **omit the FYI — No Action Needed section** from the evening email; it adds noise and is already visible in todo.md
- If no new items were extracted, say so in one line — don't skip the section
- Keep the sign-off warm and brief

---

## Sending the Email

Use the `gmail` MCP server:

```
Tool: gmail_send_messages
Input:
  to: "[user's email address]"
  subject: "[subject line from template above]"
  content: "[rendered email body as plain text]"
```

Always send the email **before** displaying the in-chat version, so the user gets the email even if they're not looking at the chat.
