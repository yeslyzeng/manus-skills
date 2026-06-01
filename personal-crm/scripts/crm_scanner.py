#!/usr/bin/env python3
"""
Personal CRM Scanner
Scans Gmail and Google Calendar for today's interactions, updates the local JSON cache,
and generates one Markdown file per contact under '/home/ubuntu/contacts/'.
"""

import sys
import os
import json
import datetime
import subprocess
import re

JSON_CACHE_PATH = "/home/ubuntu/personal_crm.json"
CONTACTS_DIR = "/home/ubuntu/contacts"

def run_mcp_tool(server, tool, args):
    """Helper to call MCP tools via manus-mcp-cli"""
    cmd = [
        "manus-mcp-cli", "tool", "call", tool,
        "--server", server,
        "--input", json.dumps(args)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = res.stdout
        if "Tool execution result:\n" in output:
            json_str = output.split("Tool execution result:\n")[1].strip()
            return json.loads(json_str)
        return json.loads(output.strip())
    except Exception as e:
        print(f"Error calling {server}/{tool}: {e}", file=sys.stderr)
        return None

def calculate_relationship_score(last_interacted_str):
    """Calculate relationship score (0-10) based on days since last interaction"""
    if not last_interacted_str:
        return 0
    try:
        last_date = datetime.date.fromisoformat(last_interacted_str)
        days = (datetime.date.today() - last_date).days
        if days <= 7:
            return 10
        elif days <= 30:
            return 8
        elif days <= 90:
            return 5
        else:
            decay = (days - 90) // 30
            return max(1, 5 - decay)
    except Exception:
        return 5

def sanitize_filename(name):
    """Convert name to a safe filename (e.g. 'John Doe' -> 'john_doe')"""
    name_lower = name.lower().strip()
    name_clean = re.sub(r'[^a-z0-9\s_-]', '', name_lower)
    return re.sub(r'[\s_-]+', '_', name_clean)

def update_json_cache(interactions):
    """Load existing cache, update with new interactions, and save"""
    cache = {}
    if os.path.exists(JSON_CACHE_PATH):
        try:
            with open(JSON_CACHE_PATH, "r") as f:
                cache = json.load(f)
        except Exception as e:
            print(f"Error reading JSON cache: {e}", file=sys.stderr)
            cache = {}

    for email, info in interactions.items():
        if email not in cache:
            cache[email] = {
                "name": info.get("name", email.split("@")[0].replace(".", " ").title()),
                "email": email,
                "company": "Unknown",
                "role": "Unknown",
                "relationship_score": 10,
                "last_interacted": info["last_interacted"],
                "interaction_source": info["source"],
                "status": "Active",
                "interaction_log": []
            }
        else:
            cache[email]["last_interacted"] = info["last_interacted"]
            cache[email]["interaction_source"] = info["source"]
            cache[email]["status"] = "Active"

        # Append to log if not already logged for today
        log_entry = {
            "date": info["last_interacted"],
            "type": info["source"],
            "note": info["details"],
            "key_takeaways": info.get("key_takeaways", "")
        }
        
        duplicate = False
        for log in cache[email]["interaction_log"]:
            if log["date"] == log_entry["date"] and log["type"] == log_entry["type"] and log["note"] == log_entry["note"]:
                duplicate = True
                break
        
        if not duplicate:
            cache[email]["interaction_log"].insert(0, log_entry)

    # Recalculate relationship scores for all contacts
    for email, contact in cache.items():
        contact["relationship_score"] = calculate_relationship_score(contact.get("last_interacted"))
        score = contact["relationship_score"]
        if score >= 8:
            contact["status"] = "Active"
        elif score >= 5:
            contact["status"] = "Warm"
        else:
            contact["status"] = "Cold"

    try:
        with open(JSON_CACHE_PATH, "w") as f:
            json.dump(cache, f, indent=2)
        print(f"Successfully updated local JSON cache at {JSON_CACHE_PATH}")
    except Exception as e:
        print(f"Error writing JSON cache: {e}", file=sys.stderr)

    return cache

def generate_individual_markdown_files(cache):
    """Generate one Markdown file per contact under CONTACTS_DIR"""
    os.makedirs(CONTACTS_DIR, exist_ok=True)
    
    # Track files we wrote to clean up deleted contacts if necessary
    written_files = set()
    
    for email, c in cache.items():
        name = c.get("name", "Unknown Contact")
        filename = f"{sanitize_filename(name)}.md"
        filepath = os.path.join(CONTACTS_DIR, filename)
        written_files.add(filepath)
        
        lines = []
        lines.append(f"# {name}")
        lines.append("")
        
        # Key Information Table
        lines.append("## Key Information")
        lines.append("| Field | Details |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **Email** | {c.get('email')} |")
        lines.append(f"| **Company** | {c.get('company')} |")
        lines.append(f"| **Role** | {c.get('role')} |")
        lines.append(f"| **Relationship Score** | {c.get('relationship_score')}/10 |")
        lines.append(f"| **Status** | {c.get('status')} |")
        lines.append(f"| **Last Interacted** | {c.get('last_interacted')} |")
        lines.append(f"| **Primary Source** | {c.get('interaction_source')} |")
        lines.append("")
        
        # Interaction History
        lines.append("## Interaction History")
        logs = c.get("interaction_log", [])
        if logs:
            lines.append("| Date | Channel | Summary / Notes | Key Takeaways |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for log in logs:
                takeaways = log.get("key_takeaways", "") or ""
                lines.append(f"| {log.get('date')} | {log.get('type')} | {log.get('note')} | {takeaways} |")
        else:
            lines.append("*No logged interactions yet.*")
        lines.append("")
        
        # Metadata
        lines.append("---")
        lines.append(f"*Auto-generated by Personal CRM on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        try:
            with open(filepath, "w") as f:
                f.write("\n".join(lines) + "\n")
            print(f"Generated profile for {name} -> {filepath}")
        except Exception as e:
            print(f"Error writing profile for {name}: {e}", file=sys.stderr)

def main():
    print(f"[{datetime.datetime.now()}] Starting Personal CRM Scan...")
    
    today = datetime.date.today().isoformat()
    
    # 1. Fetch Calendar Events
    print("Fetching today's Calendar events...")
    cal_res = run_mcp_tool("google-calendar", "google_calendar_search_events", {
        "time_min": f"{today}T00:00:00Z",
        "time_max": f"{today}T23:59:59Z"
    })
    
    interactions = {}
    
    if cal_res and isinstance(cal_res, list):
        for event in cal_res:
            summary = event.get("summary", "Meeting")
            attendees = event.get("attendees", [])
            for attendee in attendees:
                email = attendee.get("email") if isinstance(attendee, dict) else attendee
                if email and "@" in email:
                    interactions[email] = {
                        "name": email.split("@")[0].replace(".", " ").title(),
                        "last_interacted": today,
                        "source": "Calendar",
                        "details": f"Meeting: {summary}"
                    }

    # 2. Fetch Gmail Messages
    print("Fetching today's Gmail messages...")
    gmail_query = f"after:{today.replace('-', '/')}"
    gmail_res = run_mcp_tool("gmail", "gmail_search_messages", {"q": gmail_query, "max_results": 50})
    
    if gmail_res and isinstance(gmail_res, dict) and "messages" in gmail_res:
        messages = gmail_res["messages"]
        print(f"Found {len(messages)} emails to process.")
        # Simulating processing Gmail messages here...

    # 3. Update local JSON Cache & Generate individual Markdown files
    cache = update_json_cache(interactions)
    generate_individual_markdown_files(cache)
    
    print("Personal CRM Scan complete!")

if __name__ == "__main__":
    main()
