# AnalytixAI Feature Setup Instructions

You have successfully implemented the following new features:
1.  **Email Verification System**
2.  **Password Reset Functionality**
3.  **Enhanced Error Handling**
4.  **Admin Dashboard**

To make these features work, please follow these steps:

## 1. Install New Dependencies
Open your terminal in the `backend` directory and run:
```bash
cd backend
pip install -r requirements.txt
```
This installs `aiosmtplib` and other required packages.

## 2. Configure Environment Variables
Create or update your `.env` file in the `backend` directory with the following keys (see `.env.template` for reference):

```env
# Email Configuration (Gmail Example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate from Google Account > Security > App Passwords
FROM_EMAIL=your-email@gmail.com
FROM_NAME=AnalytixAI

# Frontend URL (For links in emails)
FRONTEND_URL=http://127.0.0.1:5500/frontend  # Adjust if serving differently

# Admin Configuration
ADMIN_EMAIL=admin@analytixai.com  # The user with this email will see Admin Panel
```

> **Note:** For Gmail, you MUST enable 2-Factor Authentication and generate an **App Password**. Do not use your regular password.

## 3. Create an Admin User
Since the admin logic is based on the `is_admin` flag in MongoDB:
1.  Register a new user with the email you set as `ADMIN_EMAIL` in `.env` (e.g., `admin@analytixai.com`).
2.  Manually update this user in MongoDB Compass/Atlas:
    *   Find the user document.
    *   Add a field: `is_admin: true` (Boolean).
    *   Add a field: `is_verified: true` (Boolean).

Once logged in as this user, you will see the **Admin** link in the sidebar.

## 4. Testing the Features
*   **Email Verification:** Register a new account. Check your email (or spam folder) for the verification link.
*   **Password Reset:** Click "Forgot Password?" on the login screen.
*   **Admin Panel:** Login as the admin user and access the dashboard from the sidebar.

## 5. Troubleshooting
*   **Email Errors:** Check the backend terminal logs. If connection fails, verify your SMTP credentials and App Password.
*   **Admin Link Missing:** Ensure `is_admin` is set to `true` in MongoDB and you re-logged in.
