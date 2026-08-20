# Google Forms Integration Guide — CampusDesk AI

Follow this guide to connect your Google Form to your live **CampusDesk AI** backend engine on Render in 10 seconds.

* 📝 **Live Active Google Form Submission**: **[https://forms.gle/xLJWQrskbwez9CkK8](https://forms.gle/xLJWQrskbwez9CkK8)**
* ⚡ **Live Webhook Endpoint**: `https://campusdesk-ai.onrender.com/api/v1/requests/submit`

---

## ⚡ 1-Click Code Setup (Works Standalone & Bound)

Replace all text in `Code.gs` with the snippet below (pre-configured with your Form ID `1g31b_zlhdiU70s6VHGnuevngHWjF-9ZazlbGibDmbWg`):

```javascript
function setupTrigger() {
  // Your Google Form ID
  var formId = "1g31b_zlhdiU70s6VHGnuevngHWjF-9ZazlbGibDmbWg";
  var form = FormApp.openById(formId);
  
  // Clean up any old triggers
  var triggers = ScriptApp.getUserTriggers(form);
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }

  ScriptApp.newTrigger('processFormSubmission')
      .forForm(form)
      .onFormSubmit()
      .create();
  Logger.log("✅ Trigger created successfully for Google Form!");
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

## 🚀 How to Run:
1. Copy-paste the code above into `Code.gs` and save (`Ctrl + S`).
2. Select **`setupTrigger`** from the top dropdown menu $\rightarrow$ Click **▶ Run**.
3. Click **Review permissions** $\rightarrow$ **Allow**.
4. You're done! Any submission on the Google Form will now route directly to **Render**!
