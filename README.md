# Naukri Auto Apply Bot

This project automates:

- Login to Naukri
- Resume upload
- Auto apply to recommended jobs
- AI-based question answering using Groq API + Llama model

## Project Structure

```bash
naukri-auto-apply-bot/
│
├── src/
│   └── main.py
│
├── requirements.txt
├── .env.example
├── resume.txt
└── README.md
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your-github-repo-url>
cd naukri-auto-apply-bot
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Playwright Browsers

```bash
playwright install
```

---

## 5. Configure Environment Variables

Rename:

```bash
.env.example
```

to:

```bash
.env
```

Then update:

```env
USER_EMAIL=your_email@example.com
USER_PASSWORD=your_password
API_KEY=your_groq_api_key
RESUME_PATH=C:\Users\YourName\Downloads\resume.pdf
```

---

## 6. Add Resume Text File

Create:

```bash
resume.txt
```

Paste your resume content inside it.
Add details which will ask frequently (which is not included in resume like city you are avaialable, package looking for ..soon)

---

# Run Script

```bash
python src/main.py
```

---

# Features

- Automated Naukri login
- Resume upload
- Auto apply jobs
- AI-generated answers
- Handles text/radio/checkbox questions
- Auto skips stuck applications

---

# Notes

- Keep Chrome updated
- Captcha/OTP may require manual action
- Use responsibly to avoid account restrictions

---

# API Used

- Groq API
- Model: llama-3.3-70B-Versatile
