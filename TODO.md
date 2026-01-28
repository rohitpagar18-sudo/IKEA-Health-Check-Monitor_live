# IKEA Health Check - Email Integration Task

## Task Overview
Add a separate file for sending emails using win32 library (Outlook) with specified sender and recipient emails.

## Completed Tasks
- [x] Create `email_sender_win32.py` file using win32com.client for Outlook email sending
- [x] Set sender email to "Rohit.AvinashPagar@cognizant.com"
- [x] Set recipient email to "Sksahil.Sakil@cognizant.com"
- [x] Make sender and recipient easily configurable at the top of the file
- [x] Add pywin32>=306 to requirements.txt for win32com support
- [x] Include convenience functions for sending alerts and recovery emails
- [x] Add test functionality to verify email sending
- [x] Test email functionality (found Outlook configuration issue)

## Files Created/Modified
- `email_sender_win32.py` - New email sender module using Outlook
- `requirements.txt` - Added pywin32 dependency

## Test Results
- **Status**: Code created successfully, but Outlook not configured
- **Error**: "Cannot create the email message because a data file to send and receive messages cannot be found"
- **Issue**: Microsoft Outlook needs to be properly set up with an email account on this system

## Usage
To use the new email sender:
1. Install dependencies: `pip install -r requirements.txt`
2. **Configure Outlook**: Set up Outlook with an email account (Control Panel > Mail > Show Profiles)
3. Import in your code: `from email_sender_win32 import send_alert, send_recovery`
4. To change sender/recipient, edit the variables at the top of `email_sender_win32.py`

## Notes
- Uses Microsoft Outlook via win32com.client
- Sender and recipient can be easily changed by modifying the variables at the top of the file
- Includes logging for debugging email sending issues
- Provides both class-based and functional interfaces
- **Requires Outlook to be configured with an email account to function**
