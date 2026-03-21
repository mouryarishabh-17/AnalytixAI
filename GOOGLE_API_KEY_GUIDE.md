# 🔑 How to Create a Google Gemini API Key

Follow these simple steps to get your **FREE** API key for the chat feature.

## 1. Go to Google AI Studio
Click this link: **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**

## 2. Sign In
*   Log in with your **Google Account** (Gmail).
*   If it asks, agree to the *Terms of Service*.

## 3. Create the Key
1.  Look for a big blue button that says **"Create API key"** (usually on the top left).
2.  A menu will pop up. Click **"Create API key in new project"**.
    *   *Note: This automatically sets up a project for you.*
3.  Wait a few seconds...

## 4. Copy Your Key
1.  You will see a long string of random characters starting with `AIza...`
2.  Click the **Copy** button (clipboard icon) next to it.
    *   *⚠️ Keep this key secret! Don't share it publicly.*

---

## 5. Add Key to Your Project
Now that you have the key, let's put it in your code:

1.  Open your project folder.
2.  Navigate to `backend/.env`.
3.  Find this line:
    ```env
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```
4.  Delete `YOUR_GEMINI_API_KEY_HERE` and paste your new key:
    ```env
    GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```
5.  **Save the file.**

## 6. Restart Backend
For the changes to take effect, you must restart your server:
1.  Go to your terminal where `uvicorn` is running.
2.  Press **Ctrl + C** to stop it.
3.  Run the command again:
    ```powershell
    uvicorn main:app --reload
    ```

🎉 **That's it! Your AI Chat is now ready to use.**
