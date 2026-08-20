# Google Forms Integration Guide — CampusDesk AI

Follow this guide to connect any Google Form to your live **CampusDesk AI** backend engine in 2 minutes.

* 📝 **Live Active Google Form Submission**: **[https://forms.gle/xLJWQrskbwez9CkK8](https://forms.gle/xLJWQrskbwez9CkK8)**
* ⚡ **Live Webhook Endpoint**: `https://campusdesk-ai.onrender.com/api/v1/requests/submit`

---

## 📋 Step 1: Create Your Google Form

Create a Google Form with these 5 fields (any order):

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
function setupTrigger() {
  var form = FormApp.getActiveForm();
  
  // Clean up any old existing triggers first
  var triggers = ScriptApp.getUserTriggers(form);
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }

  ScriptApp.newTrigger('processFormSubmission')
      .forForm(form)
      .onFormSubmit()
      .create();
  Logger.log("✅ Trigger created successfully!");
}

function processFormSubmission(e) {
  var BACKEND_URL = "https://campusdesk-ai.onrender.com/api/v1/requests/submit";

  var itemResponses = e.response.getItemResponses();
  var payload = {
    "student_name": "",
    "student_id": "",
    "contact_email": "",
    "department": "",
    "raw_text": ""
  };

  for (var i = 0; i < itemResponses.length; i++) {
    var title = itemResponses[i].getItem().getTitle().toLowerCase();
    var response = itemResponses[i].getResponse();

    if (title.indexOf("name") !== -1) {
      payload["student_name"] = response;
    } else if (title.indexOf("roll") !== -1 || title.indexOf("id") !== -1) {
      payload["student_id"] = response;
    } else if (title.indexOf("email") !== -1) {
      payload["contact_email"] = response;
    } else if (title.indexOf("department") !== -1) {
      payload["department"] = response;
    } else if (title.indexOf("detail") !== -1 || title.indexOf("request") !== -1 || title.indexOf("reason") !== -1) {
      payload["raw_text"] = response;
    }
  }

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    var res = UrlFetchApp.fetch(BACKEND_URL, options);
    Logger.log("CampusDesk AI Response: " + res.getContentText());
  } catch (err) {
    Logger.log("Error dispatching to CampusDesk AI: " + err.toString());
  }
}
```

---

## ⏰ Step 3: Run `setupTrigger` (Or Add Trigger via UI)

### Method A (Code Setup):
1. Select **`setupTrigger`** from the top dropdown menu $\rightarrow$ Click **▶ Run**.
2. Click **Review permissions** $\rightarrow$ **Allow**.

### Method B (Visual UI Setup):
1. Click the **⏰ Triggers icon** on the left menu bar in Google Apps Script.
2. Click **+ Add Trigger** (bottom right).
3. Set **Choose which function to run**: `processFormSubmission`.
4. Set **Select event source**: `From form`.
5. Set **Select event type**: `On form submit`.
6. Click **Save**.
