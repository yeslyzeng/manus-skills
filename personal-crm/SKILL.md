---
name: personal-crm
description: "Personal CRM management with automated daily scanning and weekly follow-up recommendations. Use for syncing contacts from Gmail/Google Calendar to local individual Markdown files, updating interaction logs, calculating relationship scores, and generating personalized catch-up recommendations."
---

# Personal CRM (Agent-Native)

This skill enables an **agent-native Personal CRM** system optimized for managing personal and professional relationships. It automates contact discovery, relationship scoring, interaction logging, and follow-up recommendations by integrating with **Gmail**, **Google Calendar**, and generating a clean directory of **individual Markdown profiles** under `/home/ubuntu/contacts/`.

---

## Agent-Native Context Architecture

To ensure speed, reliability, and modularity, this CRM uses a **dual-layer storage and presentation architecture**:

1.  **Local Structured Memory (`/home/ubuntu/personal_crm.json`)**:
    *   **Primary Source of Truth**: This is the agent's fast, local long-term memory containing all contacts and their full interaction logs.
    *   **Performance**: Querying local JSON is instant and consumes zero external API tokens or credits.
    *   **Persistence**: The sandbox filesystem is persistent across hibernation cycles, making this local file highly reliable.
2.  **Individual Markdown Profiles (`/home/ubuntu/contacts/{sanitized_name}.md`)**:
    *   **User Interface**: Every contact has a dedicated, beautiful profile document in GitHub-flavored Markdown.
    *   **Sync Direction**: The local JSON cache is compiled and written directly to these individual files after every daily scan.
    *   **Content**: Each file includes a Key Information Table (Email, Company, Role, Score, Status, Last Interacted) and a complete chronological table of Interaction History.

---

## Core Capabilities & Schedule Mapping

The Personal CRM relies on two automated schedules. Because the system allows one schedule per task, each schedule must be created in its own dedicated task. The local JSON cache at `/home/ubuntu/personal_crm.json` is the shared persistent state that both tasks read and write.

| Time (Local) | Routine | Description | Task Setup |
| :--- | :--- | :--- | :--- |
| **06:00 PM daily** | **Evening Scan** | Scans today's Gmail and Calendar, updates the local cache, generates/updates individual contact Markdown files. | Create a dedicated task titled "Personal CRM Daily Scan" and run: `manus-config schedule create --title "Personal CRM Daily Scan" --cron "0 0 18 * * *" --repeated --detail "<see Workflow A below>"` |
| **Monday 09:00 AM** | **Weekly Recommendations** | Reads the local cache, identifies overdue contacts, drafts catch-up emails. | Create a separate dedicated task titled "Personal CRM Weekly Recommendations" and run: `manus-config schedule create --title "Personal CRM Weekly Recommendations" --cron "0 0 9 * * 1" --repeated --detail "<see Workflow B below>"` |

> **Important**: Both tasks share `/home/ubuntu/personal_crm.json` as their persistent memory. This file is the single source of truth — the daily scan writes to it, and the weekly task reads from it. Always initialize it as `{}` if it does not exist.

---

## Workflow A: Daily Evening Scan (06:00 PM)

Every evening at 6:00 PM local time, perform the following steps sequentially:

### Step 1: Fetch and Extract Today's Interactions
1.  **Google Calendar**: Call `google_calendar_search_events` with `time_min` and `time_max` set to today's date range.
    *   Extract attendee names and email addresses.
    *   Ignore the user's own email and common internal domains (e.g., `@manus.im`).
2.  **Gmail**: Call `gmail_search_messages` with the query `after:{today_date}`.
    *   Fetch the threads using `gmail_read_threads`.
    *   Extract sender and recipient email addresses.

### Step 2: Update Local JSON Cache
1.  Read the existing CRM data from `/home/ubuntu/personal_crm.json`. (Initialize as `{}` if the file does not exist).
2.  For each extracted contact:
    *   Update `last_interacted` to today's date.
    *   Update `interaction_source` (e.g., `Gmail` or `Calendar`).
    *   Append today's interaction context (e.g., "Meeting: Product Sync" or "Email: Proposal Feedback") to their interaction history log.
    *   If meeting notes, calendar event descriptions, or email body content are available, extract and summarize 1-2 sentences of **Key Takeaways** (decisions made, action items, topics discussed) and store them in the `key_takeaways` field of the log entry. Leave blank if no content is available.
    *   Recalculate their **Relationship Score** (0-10) using the scoring matrix.
3.  Save the updated data back to `/home/ubuntu/personal_crm.json`.

### Step 3: Generate Individual Contact Markdown Profiles
1.  Read the entire cache from `/home/ubuntu/personal_crm.json`.
2.  Ensure the directory `/home/ubuntu/contacts/` exists.
3.  For each contact in the cache, sanitize their name to create a safe filename (e.g., `John Doe` -> `/home/ubuntu/contacts/john_doe.md`).
4.  Generate or overwrite the file with:
    *   **Contact Name** as the H1 title.
    *   **Key Information Table**: Email, Company, Role, Score, Status, Last Interacted, and Primary Source.
    *   **Interaction History Table**: A structured pipe table listing Date, Channel, Summary / Notes, and **Key Takeaways** (1-2 sentence summary of decisions, action items, or topics discussed; blank if no notes available) for every interaction.

---

## Workflow B: Weekly Recommendations (Monday 09:00 AM)

Every Monday morning at 9:00 AM local time, perform the following steps:

### Step 1: Identify Overdue Contacts
1.  Read the local CRM cache from `/home/ubuntu/personal_crm.json`.
2.  For each contact, determine their **Follow-Up Frequency** based on their Relationship Score:
    *   **Score 8-10 (Tier 1 - VIP)**: Follow up every **14 days**.
    *   **Score 5-7 (Tier 2 - Warm)**: Follow up every **30 days**.
    *   **Score 1-4 (Tier 3 - Casual)**: Follow up every **90 days**.
3.  Calculate the days elapsed since `last_interacted`. If `elapsed_days` > `frequency_days`, mark the contact as **Overdue**.

### Step 2: Select Top 5 Recommendations
1.  Sort all Overdue contacts by their overdue gap (`elapsed_days - frequency_days`) in descending order.
2.  Select the top 5 contacts.
3.  For each of the top 5 contacts, extract their recent interaction history from the local cache to build context.

### Step 3: Draft Personalized Outreach Emails
1.  For each recommended contact, draft a warm, personalized catch-up email.
2.  Incorporate context from their last interaction (e.g., "Great chatting at our last meeting about X. Hope everything is going well with that!").
3.  Keep the tone warm, professional, and low-pressure.

### Step 4: Present Weekly Report
Output a clean, beautifully formatted Markdown report containing:
1.  **Weekly Summary Table**: High-level stats of the CRM (total contacts, active, overdue).
2.  **Top 5 Follow-Up Recommendations**: Detailed cards for each person showing their score, last interaction date, and overdue days.
3.  **Draft Outreach Emails**: Ready-to-send draft emails that the user can copy or have the agent send.

---

## Local JSON Cache Schema (`/home/ubuntu/personal_crm.json`)

The local cache is a JSON object keyed by the contact's email address. This is the canonical data model the agent reads and writes:

```json
{
  "john.doe@acme.com": {
    "name": "John Doe",
    "email": "john.doe@acme.com",
    "company": "Acme Corp",
    "role": "VP of Engineering",
    "relationship_score": 8,
    "last_interacted": "2026-05-20",
    "interaction_source": "Calendar",
    "status": "Active",
    "interaction_log": [
      {"date": "2026-05-20", "type": "Calendar", "note": "Meeting: Q2 Planning Sync",          "key_takeaways": "Agreed to move launch to Q3; John to send revised timeline by Friday."},
      {"date": "2026-04-10", "type": "Gmail",    "note": "Email: Contract renewal discussion", "key_takeaways": "Pricing concern raised; offered 10% discount for annual commitment."}
    ]
  }
}
```

---

## Dynamic Relationship Scoring Matrix (0-10)

Scores are calculated dynamically based on interaction frequency and warmth:

| Score | Category | Frequency Signal | Recalculation Rule |
| :--- | :--- | :--- | :--- |
| **9-10** | **Strategic / VIP** | Weekly multi-turn emails or calendar meetings. | Set automatically if interacted within last 7 days. |
| **7-8** | **Active / Warm** | Monthly emails or calendar meetings. | Set automatically if interacted within last 30 days. |
| **5-6** | **Regular Network** | Quarterly interactions. | Set automatically if interacted within last 90 days. |
| **1-4** | **Cold / Inactive** | No interactions for >90 days. | Score decays by 1 point for every 30 days of inactivity. |

---

## Resources

*   **`scripts/crm_scanner.py`**: Python execution script that handles the daily Gmail/Calendar parsing, local JSON cache updates, and generating individual contact Markdown profiles.
*   **`references/design.md`**: Architectural design and Markdown template details.
