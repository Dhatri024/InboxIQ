# InboxIQ – AI-Powered Email Intelligence Platform

## Overview

InboxIQ is an AI-powered email intelligence platform that helps users quickly understand and prioritize emails. The system analyzes email content and generates actionable insights including summaries, sentiment analysis, urgency detection, smart replies, keyword extraction, and email classification.

The project consists of:

* A React-based web application
* A Chrome Extension for Gmail integration
* A FastAPI backend powered by Transformer-based AI models
* Cloud deployment using Vercel and Hugging Face Spaces

---

## Features

### Email Analysis

* AI-generated email summaries
* Sentiment analysis
* Urgency detection
* Priority scoring
* Email categorization
* Email type detection

### Productivity Features

* Smart reply generation
* Action item extraction
* Reminder suggestions
* Keyword extraction
* Entity extraction

### User Interfaces

* Responsive React web application
* Chrome Extension for Gmail email extraction
* Real-time AI analysis dashboard

---

## System Architecture

```text
┌─────────────────────┐
│      Gmail Email    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Chrome Extension    │
│ Email Extraction    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ React Frontend      │
│ (Vercel)            │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│ FastAPI Backend     │
│ (Hugging Face)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Processing Layer │
│ Transformers Models │
└─────────────────────┘
```

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Browser Extension

* Chrome Extension API
* JavaScript
* HTML
* CSS

### Backend

* Python
* FastAPI
* Uvicorn

### AI & NLP

* Hugging Face Transformers
* DistilBART CNN (Summarization)
* DistilBERT Sentiment Analysis
* FLAN-T5 (Smart Reply Generation)
* BART Large MNLI (Classification)

### Deployment

* Vercel (Frontend)
* Hugging Face Spaces (Backend)
* GitHub (Version Control)

---

## Project Structure

```text
InboxIQ/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── main.py
│
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
│
└── README.md
```

---

## Workflow

1. User enters or extracts an email.
2. Frontend sends the email content to the FastAPI backend.
3. AI models process the email.
4. Backend generates:

   * Summary
   * Sentiment
   * Urgency
   * Priority Score
   * Smart Reply
   * Keywords
   * Entities
   * Action Items
5. Results are displayed in the web application or extension.

---

## Sample Output

### Input Email

```text
Hi Team,

We have an urgent meeting tomorrow regarding the project deadline.
Please prepare the updated report and share it before 5 PM.

Regards,
Manager
```

### Generated Results

**Summary**

* Brief summary of the email content

**Sentiment**

* Positive / Negative

**Urgency**

* High

**Category**

* Work

**Action Items**

* Prepare updated report
* Share report before deadline

**Smart Reply**

* AI-generated professional response

---
## Results

The InboxIQ platform successfully analyzes email content and generates intelligent insights in real time.

### Generated Outputs

| Feature              | Output                                          |
| -------------------- | ----------------------------------------------- |
| Email Summary        | Concise AI-generated summary of email content   |
| Sentiment Analysis   | Positive / Negative classification              |
| Urgency Detection    | High, Medium, or Low urgency level              |
| Priority Score       | Numerical priority estimation                   |
| Email Category       | Work, Meeting, Finance, Personal, Spam, Support |
| Email Type           | Context-based email classification              |
| Action Items         | Extracted actionable tasks from email           |
| Keywords             | Important terms identified from email           |
| Entities             | Proper nouns and important entities detected    |
| Reminder Suggestions | Recommended reminder actions                    |
| Smart Reply          | AI-generated professional email response        |

### Performance Highlights

* Real-time email analysis through FastAPI backend
* Transformer-based NLP models for intelligent processing
* Gmail email extraction through Chrome Extension
* Responsive React web interface
* Cloud deployment using Vercel and Hugging Face Spaces

### Example Analysis

**Input Email**

```text
Hi Team,

We have an urgent meeting tomorrow regarding the project deadline.
Please prepare the updated report and share it before 5 PM.

Regards,
Manager
```

**Generated Results**

* Summary: Email discusses an urgent meeting and project deadline.
* Sentiment: Negative
* Urgency: High
* Category: Work
* Action Items:

  * Prepare updated report
  * Share report before 5 PM
* Smart Reply:

  * A professional AI-generated response suitable for replying to the sender.

### Screenshots

<img width="1430" height="678" alt="Screenshot 2026-06-25 at 6 41 06 PM" src="https://github.com/user-attachments/assets/ec2e201f-31fb-4cb6-adf1-f25c9014ff72" />

<img width="1430" height="878" alt="Screenshot 2026-06-25 at 6 32 08 PM" src="https://github.com/user-attachments/assets/0e2bea35-fc30-41de-8862-674aeaa4bdee" />

<img width="1000" height="500" alt="Screenshot 2026-06-25 at 6 33 40 PM" src="https://github.com/user-attachments/assets/5c42f1a1-164c-4cf6-9702-332180ba7310" />
<img width="400" height="600" alt="Screenshot 2026-06-25 at 6 35 04 PM" src="https://github.com/user-attachments/assets/e7b09d98-20ab-44ad-a6b7-71699f2ed946" />
<img width="400" height="600" alt="Screenshot 2026-06-25 at 6 36 16 PM" src="https://github.com/user-attachments/assets/d9b632bd-fc65-461e-bc88-d012bcca12e8" />

<img width="400" height="600" alt="Screenshot 2026-06-25 at 6 36 47 PM" src="https://github.com/user-attachments/assets/24d03fa7-44ca-47fd-bfa6-2b0da9fd6e59" />


## Deployment Links

### Frontend

https://inbox-iq-sandy.vercel.app

### Backend API

https://dhatri-02-inboxiq-backend.hf.space

### API Documentation

https://dhatri-02-inboxiq-backend.hf.space/docs

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Dhatri024/InboxIQ.git
cd InboxIQ
```

### Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

### Chrome Extension Setup

1. Open Chrome
2. Navigate to:

```text
chrome://extensions
```

3. Enable Developer Mode
4. Click Load Unpacked
5. Select the `extension` folder

---

## Future Improvements

* Chrome Web Store publication
* Advanced email ranking
* Multi-language email support
* Calendar integration
* Automated email tagging
* Enhanced entity recognition
  
---
title: InboxIQ Backend
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# InboxIQ Backend
