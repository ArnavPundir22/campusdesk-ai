# Google Forms Integration Guide — CampusDesk AI

Follow this guide to connect any Google Form to your live **CampusDesk AI** backend engine in 3 minutes.

---

## 📋 Step 1: Create Your Google Form

Create a new Google Form with these 5 fields (in exact order):

1. **Student Full Name** *(Short answer)*
2. **Student Roll / ID Number** *(Short answer)*
3. **Contact Email Address** *(Short answer)*
4. **Department** *(Dropdown or Short answer)*
5. **Request Details** *(Paragraph — unstructured request, leave reasons, budget reimbursement specs, or lab borrowing)*

---

## ⚡ Step 2: Add Google Apps Script Webhook

1. Open your Google Form.
2. Click the **`⋮` (Three dots)** icon in the top-right corner $\rightarrow$ Click **Script editor** (or **Apps Script**).
3. Delete any default code in `Code.gs` and paste the following snippet:

```javascript
function onFormSubmit(e) {
  // REPLACE WITH YOUR CAMPUSDESK AI SERVER URL
  // For local testing via ngrok: "https://xxxx.ngrok-free.app/api/v1/requests/submit"
  // For production: "https://your-domain.com/api/v1/requests/submit"
  var BACKEND_URL = "https://YOUR_SERVER_URL/api/v1/requests/submit";

  var itemResponses = e.response.getItemResponses();

  var payload = {
    "student_name": itemResponses[0] ? itemResponses[0].getResponse() : "",
    "student_id": itemResponses[1] ? itemResponses[1].getResponse() : "",
    "contact_email": itemResponses[2] ? itemResponses[2].getResponse() : "",
    "department": itemResponses[3] ? itemResponses[3].getResponse() : "",
    "raw_text": itemResponses[4] ? itemResponses[4].getResponse() : ""
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch(BACKEND_URL, options);
    Logger.log("CampusDesk AI Response: " + response.getContentText());
  } catch (err) {
    Logger.log("Error dispatching to CampusDesk AI: " + err.toString());
  }
}
```

---

## ⏰ Step 3: Enable the "On Form Submit" Trigger

1. In the Apps Script left sidebar, click **Triggers** 🕒 *(alarm clock icon)*.
2. Click **+ Add Trigger** (bottom-right).
3. Configure trigger options:
   - **Choose which function to run:** `onFormSubmit`
   - **Select event source:** `From form`
   - **Select event type:** `On form submit`
4. Click **Save** and grant permissions.

---

## 🎉 Done! How It Works Real-Time

- When a student fills out the Google Form, Google Apps Script automatically forwards the response to **CampusDesk AI**.
- **Gemini 2.5 Flash** parses the submission text.
- Deterministic rules categorize and approve/gate the request.
- Notion cards and Run Logs update live in your Notion workspace!
