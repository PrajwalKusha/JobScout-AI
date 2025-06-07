# 💼 JobScout AI

**Your AI-Powered Job Matching Assistant**  
Match your resume to real-time job listings, get intelligent suggestions, download results, and email them — all in one place.

![JobScout AI Banner](![Screenshot 2025-06-07 at 5 24 46 PM](https://github.com/user-attachments/assets/4c04b4d9-723c-4d57-ae79-835661c53795)) <!-- Optional banner -->

---

## 🚀 Overview

**JobScout AI** is an end-to-end, AI-driven job matching web app that helps job seekers understand how well their resume fits specific roles. It parses resumes using GPT-3.5 Turbo (via OpenRouter), scrapes job listings from Indeed, compares the skillset, and provides:

- Match Score  
- Matched & Missing Skills  
- Suggestions for improvement  
- Downloadable CSV results  
- Email delivery of results using Twilio SendGrid

⚡ **Live Frontend Demo:** [https://prajwalkusha.vercel.app](https://prajwalkusha.vercel.app)  
🛠️ **Full functionality (including scraping and AI) requires local backend**

---

## ✨ Features

- 📄 Upload your resume (PDF)
- 🔎 Search job listings by role & location
- 🤖 Get AI-generated skill match analysis using GPT-3.5
- 📈 Download results as `.csv`
- 📬 Send results to any email using SendGrid

---

## 🧰 Tech Stack

**Frontend:**  
- React + Vite  
- Tailwind CSS  
- shadcn/ui components

**Backend:**  
- FastAPI (Python)  
- BeautifulSoup + Selenium (Job scraping)  
- GPT-3.5 Turbo via OpenRouter (Resume parsing + matching)  
- Twilio SendGrid (Emailing)

---

## 🛠️ Installation & Local Setup

> 💡 Ensure Python 3.9+ and Node.js 16+ are installed on your system.

### 1. Clone the Repository

```bash
git clone https://github.com/prajwalkusha/JobScout-AI.git
cd JobScout-AI
```

---

### 2. Set Up Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create `.env` in `backend/` and add your keys:

```env
OPENROUTER_API_KEY=your_openrouter_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
EMAIL_FROM=youremail@domain.com       # Verified sender email (SendGrid)
```

---

### 4. Run Backend Server

```bash
uvicorn main:app --reload
```

The FastAPI server will start at `http://127.0.0.1:8000`.

---

### 5. Set Up Frontend

Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`.

---

## ⚙️ Usage Instructions

1. Visit `http://localhost:5173`
2. Upload your resume (PDF)
3. Enter the job role and location
4. Click **Search Jobs**
5. View Match Score, Skills Analysis, Suggestions
6. Click **Download CSV** or **Send Email**

---

## 📬 API Keys Required

### 🔑 OpenRouter GPT-3.5 Key

- Go to [https://openrouter.ai](https://openrouter.ai)
- Sign in and get your API key
- Add it to your `.env` file in `backend/` as `OPENROUTER_API_KEY`

### 📧 SendGrid Email Setup

- Create an account at [https://sendgrid.com](https://sendgrid.com)
- Create and verify a sender identity (email address)
- Generate an API Key under **Settings → API Keys**
- Add it to `.env` as `SENDGRID_API_KEY`
- Set the sender email as `EMAIL_FROM`

---

## 🧪 Demo Video (Coming Soon)

🎥 A short walkthrough video showing full functionality will be added soon.  
Stay tuned!

---

## 📂 Project Structure

```
JobScout-AI/
├── backend/
│   ├── main.py
│   ├── resume_parser.py
│   ├── job_scraper.py
│   ├── email_sender.py
│   └── .env
├── frontend/
│   ├── src/
│   ├── App.jsx
│   └── ...
├── README.md
└── requirements.txt
```

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
Feel free to fork this repo and propose new features or improvements.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 👋 Connect with Me

🔗 [LinkedIn – Prajwal Kusha](https://www.linkedin.com/in/prajwal-kusha)  
🌐 [Portfolio – prajwalkusha.vercel.app](https://prajwalkusha.vercel.app)

---

## 🔖 Tags

`#OpenAI` `#GPT3` `#JobSearchAI` `#FastAPI` `#Selenium` `#SendGrid` `#ResumeMatcher`
