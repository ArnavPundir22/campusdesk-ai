# design.md — Notion Workspace UI & Design Specs
## CampusDesk AI: Operations Hub Design System

---

## 1. Design Philosophy: Human-Readable Operations Hub
According to Notion Track guidelines:
> *"Turn your service off. Is the Notion workspace still a useful place to run this job? If your workspace is a dump of JSON-looking rows nobody would read, the answer is no. Build for yes."*

CampusDesk AI formats every single page inside Notion as a clean, beautifully styled executive dashboard card.

---

## 2. Page Design & Layout Architecture

### 2.1 Request Page Header & Properties
Every request card created in the **Student Requests** database features:
* **Icon:** Category-specific emoji (e.g., 📝 Leave, 💰 Budget, 🔬 Lab Equipment, 🎪 Event).
* **Cover Image:** Color gradient header based on status (Green for Approved, Yellow for Pending, Red for Rejected).
* **Database Properties Bar:**
  - `Status`: Styled select pill (`Pending Approval` | `Auto-Approved` | `Approved` | `Rejected`).
  - `Student`: Plain text name + Roll ID.
  - `Category`: Color-coded category badge.
  - `Urgency`: Red/Yellow/Blue select pill.
  - `Submitted At`: Formatted date string.

---

### 2.2 Page Body Blocks Layout

Each request page body is rendered using structured Notion blocks:

```markdown
+-------------------------------------------------------------------------------+
| 💡 EXECUTIVE SUMMARY (Callout Block - Gray Background)                        |
| "Aarav Sharma (Roll #2023-CS-042) is requesting ₹1,450 for Arduino sensors    |
| purchased for the Robotics Competition on 15th Aug."                          |
+-------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------+
| ⚙️ SYSTEM ASSESSMENT & REASONING (Toggle Heading Block)                      |
| ▶ View AI Semantic Extraction & Rule Evaluation                               |
|   • Parsed Amount: ₹1,450.00                                                  |
|   • Rule Evaluated: R4 (Budget > ₹1,000)                                      |
|   • System Action: Paused execution at Human Approval Gate                    |
+-------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------+
| 🙋 HUMAN APPROVER ACTION BOARD (Callout Block - Yellow Background)            |
| "Action Required: Please review the attached receipt details below and update |
| the Status property at the top to 'Approved' or 'Rejected'."                 |
+-------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------+
| 📄 ORIGINAL REQUEST SUBMISSION (Quote Block)                                 |
| "Sir, requesting reimbursement of Rs 1,450 spent on purchasing Arduino        |
| sensors for the Robotics Competition held on 15th Aug."                       |
+-------------------------------------------------------------------------------+
```

---

## 3. Database Views & Filters

The Notion workspace provides 3 custom database views:

1. **📥 Inbox View (All Requests):** Table view sorted by submission timestamp descending.
2. **⏳ Human Approval Queue (Board View):** Kanban board view grouped by `Status` filtered to show `Pending Approval` items in the primary column.
3. **📗 Audit & Run Log (Timeline View):** Programmatically updated database table showing exact execution timestamps, duration in milliseconds, and action logs written by backend integration tokens.
