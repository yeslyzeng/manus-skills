# Calendar and Email Triage Rules (Context-Aware Edition)

This document defines the pre-screening filters, context-aware relationship scoring matrix, cold email demotion rules, and the standard output template for the **Morning Digest (09:00 AM)**.

---

## Part 1: Email Pre-screening Filters

Before evaluating or categorizing any emails, apply these filters to exclude noise. Silently ignore and omit the following from the triage report:
- **Calendar Notifications**: Invites, updates, acceptances, declines, or reminders.
- **Access Requests**: Google Drive, Notion, Slack, Figma, or other file-sharing/access request emails.
- **Pure Automated Alerts**: System alerts, password resets, or standard subscription receipts.

---

## Part 2: Context-Aware Relationship Scoring Matrix

Do not classify emails solely based on subject lines or content urgency. Instead, evaluate the **sender's context** using the matrix below.

### Relationship Scoring Criteria

| Factor | High Score (+2) | Medium Score (+1) | Low/Zero Score (0) |
| :--- | :--- | :--- | :--- |
| **Prior History** | Active thread; the user or their team has replied to this sender in the past. | 1-way inbound but sender has reached out before; no prior replies. | No prior email history; brand new contact. |
| **Company Size & Tier** | Large/well-known enterprise, tier-1 VC/investor, major press, or key strategic partner. | Mid-market company, growing startup, or secondary partner. | Small business, individual sender, or unknown domain. |
| **Relationship with User/Org** | Existing active customer, signed partner, or warm introduction. | Qualified lead, pipeline prospect, or prospective vendor. | Cold outreach, cold sales pitch, or unsolicited inquiry. |

### Classification Routing Rules

Evaluate the total context score and content indicators to route emails into one of four standard buckets:

```
Total Context Score = Prior History Score + Company Size Score + Relationship Score
```

#### 1. URGENT (Action Required within 1 Hour)
- **Condition**: Total Context Score is **4 or higher** **AND** the email content indicates immediate commercial or operational urgency (e.g., system downtime, active contract blocker, immediate demo request from tier-1 lead).
- **Action**: Place at the top of the Morning Digest. Draft a customized, warm, and concise reply. Suggest action `[Respond]`.

#### 2. ACTION (Action Required Today)
- **Condition**: Total Context Score is **2 or 3** **AND** the email requests a specific follow-up, meeting, or response today.
- **Action**: Draft a reply and suggest adding to the to-do list. Suggest action `[Respond]`.

#### 3. FYI (Read Later, No Reply Needed)
- **Condition**: Total Context Score is **1 or 2** **AND** the email is informational (e.g., project updates, CC'd threads where teammates are active, newsletters from strategic partners).
- **Action**: Summarize in 1 sentence. Suggest action `[Archive]` or `[Do Nothing]`.

#### 4. NOISE (Archive Immediately)
- **Condition**: Total Context Score is **0** (Cold Email) **OR** the email is a generic automated notification.
- **Action**: Summarize in 1 sentence. Suggest action `[Archive]`.

---

## Part 3: The "Not Addressed to User" Demotion Rule

> **CRITICAL RULE**: If an email's **To:** field does not include the user's address as a primary recipient — meaning the email is addressed to someone else and the user is only **CC'd** or **BCC'd** — the email **MUST NEVER** be classified as URGENT or ACTION.
>
> Emails where the user is not the primary addressee are informational by nature. They belong in **FYI** at most, regardless of how urgent or important the content appears. The reasoning: if the sender needed the user to act, they would have addressed them directly.
>
> **How to apply this rule:**
> 1. Check the **To:** field of the email.
> 2. If the user's address is **not** in the To field (they are only in CC or BCC), cap the classification at **FYI**.
> 3. Summarise the FYI item naturally — do not note who it is addressed to or that the user is CC'd. The output should read as a clean status update, not a triage explanation.
> 4. If the thread has stalled and no one else has responded in 3+ days, you may escalate it to **ACTION** with a note suggesting the user nudge the primary recipient.

---

## Part 4: The Cold Email Demotion Rule

> **CRITICAL RULE**: If an email is identified as a **cold outreach** (Prior History Score = 0 AND Relationship = Cold/Unsolicited), it **MUST NEVER** be classified as URGENT or ACTION, regardless of how urgent, important, or dramatic its content sounds.
>
> Senders of cold emails often use urgent subject lines (e.g., "Urgent question regarding your API" or "Important: partnership proposal") to bypass filters. If there is no prior relationship or strategic context, the email is classified as **NOISE** or **FYI** at best.

---

## Part 5: Morning Digest In-Chat Template

When displaying the Morning Digest in-chat, use this structure. Keep it brief and skimmable.

**Note:** The email version uses the template in `references/email-templates.md`. The in-chat version may include draft replies for URGENT/ACTION items, but the NOISE section is always omitted from both.

```markdown
# Morning Digest — [Weekday, Month DD]

Good morning, [User Name]!

## 🎯 Most Important Tasks
1. **[Task]** — [one-line reason]
2. **[Task]** — [one-line reason]
3. **[Task]** — [one-line reason]

## 📅 Today
[Time] [Event] — [location]
💡 Deep work: [time block]

## 🚨 Urgent
**[Sender, Company]** — "[Subject]"
[1-2 sentence summary + suggested action]

> [Draft reply if applicable]

## 📋 Action
**[Sender, Company]** — "[Subject]"
[1 sentence + suggested action]

> [Draft reply if applicable]

## 💬 FYI
- **[Sender]** — [1-line summary]. [Who is handling.] `[Suggested action]`
- **[Sender]** — [1-line summary]. `[Suggested action]`
```

**Rules:**
- Omit NOISE entirely — do not list archived emails
- If no URGENT or ACTION emails exist, skip those sections
- FYI items are a compact bulleted list, not individual headers
- Draft replies appear in-chat only, never in the email
- **Include deep links to emails and meeting notes** — for every email mentioned in the digest, construct a Gmail deep link using the thread ID: `https://mail.google.com/mail/u/0/#inbox/{threadId}`. For Granola meeting notes referenced in FYI, construct a link using the meeting ID: `https://app.granola.ai/meetings/{meetingId}`. Embed these as Markdown hyperlinks on the sender name or subject. In the email version, include the URL as plain text after the item since email clients don't render Markdown links.
- **NEVER include triage reasoning in the output** — do not mention why an email was prioritised, who it was addressed to, context scores, or any internal classification logic. The output should read as a clean, natural summary, not a report of the triage process. For example:
  - BAD: "Addressed directly to you. Context score: 6/6. Classified as URGENT."
  - BAD: "Addressed to Chris; you are CC'd."
  - GOOD: "RSM US is reporting a live guest access bug on published webapps. Reply today."
  - GOOD: "Crunchbase trial starts Friday — ping Chris to confirm he's reviewed the agreement."
