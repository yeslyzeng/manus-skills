# Slack DM Templates for Daily Assistant

These templates are used when sending the Morning Digest and Evening Follow-up as Slack DMs to the user. Slack uses its own markdown syntax — different from email and standard Markdown.

**Slack markdown cheatsheet:**
- `*bold*` — bold
- `_italic_` — italic
- `~strikethrough~` — strikethrough
- `` `code` `` — inline code
- `>text` — blockquote
- Bullet lists: start lines with `•` or `-`
- Numbered lists: `1.`, `2.`, etc.
- Links: `<https://url|link text>`

**Slack does NOT render:** `━━━` dividers, `##` headers, `**bold**` (double asterisk), or `[text](url)` Markdown links.

---

## Morning Digest — Slack Template

Send as a single DM to the user's Slack user ID. Keep under 5000 characters; split into two messages if needed.

```
*🌅 Morning Digest — [Weekday, Month DD]*

*🎯 MOST IMPORTANT TASKS*
1. [Task] — [one-line reason]
2. [Task] — [one-line reason]
3. [Task] — [one-line reason]

*📅 CALENDAR*
[Time] [Event]
[Time] [Event]
💡 Deep work: [time block]

*📬 EMAILS*

🚨 *[Sender, Company]* — [Subject]
[1 sentence summary]
<https://mail.google.com/mail/u/0/#inbox/{threadId}|Open in Gmail>

📋 *[Sender, Company]* — [Subject]
[1 sentence summary]
<https://mail.google.com/mail/u/0/#inbox/{threadId}|Open in Gmail>

💬 *FYI*
• [Sender] — [1-line summary]
• [Sender] — [1-line summary]
```

**Rules:**
- Bold section headers on their own line, preceded by an emoji
- One blank line between sections
- No blank lines within a section — items run flush
- URGENT items get 🚨, ACTION items get 📋
- Gmail deep links formatted as `<url|Open in Gmail>` — Slack renders these as clickable hyperlinks
- Omit NOISE entirely
- Skip URGENT or ACTION sections if empty
- Never expose triage reasoning

---

## Evening Follow-up — Slack Template

Send as a single DM (or two if the to-do list is long).

```
*🌙 Evening Follow-up — [Weekday, Month DD]*

*📝 NEW ACTION ITEMS*

*[Meeting Name]* — <https://app.granola.ai/meetings/{meetingId}|Notes>
• [Action item] — [brief context / deadline]
• [Action item]

*[Meeting Name]* — <https://app.granola.ai/meetings/{meetingId}|Notes>
• [Action item]

_(No meeting notes today — nothing new to add.)_

*✅ YOUR TO-DO LIST*

*🎯 Most Important Tasks*
• [Task] — [reason]
• [Task]

*[Emoji] [Category]*
• [Task] — [context] _(🔥 urgent)_
• [Task]

*👀 FYI — No Action Needed*
• [Topic] — [1-line status]
```

**Rules:**
- Group new items by source meeting; include a Granola link formatted as `<url|Notes>`
- Full to-do list always included, organized by topic category
- Omit the FYI — No Action Needed section from the to-do list in this message (keep it clean)
- If no new items, say so in one line inside the NEW ACTION ITEMS section
- Urgency tag: `_(🔥 urgent)_` (italic in Slack)

---

## Sending via Slack MCP

```
Tool: slack_send_message
Input:
  channel_id: "[user's Slack user ID]"
  message: "[rendered message body using Slack markdown above]"
```

Always send Slack DM **before** the email and before displaying in-chat.
