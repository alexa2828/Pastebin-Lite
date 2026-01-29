# Pastebin-Lite

A simple Pastebin-like web application that allows users to create text pastes and share them via a unique URL.  
Pastes can optionally expire based on **time (TTL)** or **view count**.

Pastebin-Lite is a minimalist web application that allows users to create text pastes and share them via unique, shareable URLs. 
The application supports optional constraints, including time-based expiry (TTL) and view-count limits, ensuring pastes become unavailable once a constraint is met.
---

## Features

- Create a text paste
- Generate a shareable URL
- View a paste via API or browser
- Optional constraints:
  - Time-to-live (TTL)
  - Maximum number of views
- Automatic expiry when constraints are reached
---

## Tech Stack

- **Backend**: Python and Flask
- **Frontend**: HTML, CSS and Javascript
- **database**: MongoDB
- **Deployment**: Vercel or Render

---

##Deployed URL

Render: https://pastebin-lite-dz0w.onrender.com (It takes time to create a link)
Vercel: https://pastebin-lite-task-rust.vercel.app/ (It takes time to create a link)


###How to run the project locally
1. Clone the Repository
  Clone the project from GitHub and navigate into the project directory.

  $git clone https://github.com/alexa2828/Pastebin-Lite.git
  $cd Pastebin-Lite

2. Create a Virtual Environment (Windows)
  $python -m venv venv
  $venv\Scripts\activate

  Create a Virtual Environment (Linux / macOS)
  $python -m venv venv
  $source venv/bin/activate
 
** After activation, you should see (venv) in your terminal.**

3. Install Project Dependencies
  $pip install -r requirements.txt

4. Run the Flask Application
  $python app.py

5. Access the Application in Browser
  http://127.0.0.1:5000/


