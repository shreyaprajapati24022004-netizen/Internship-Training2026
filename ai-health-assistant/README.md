# 🩺 Cure Sphere

> **A fully private, offline AI Health Assistant powered by local LLMs using Ollama.**

Cure Sphere is an AI-powered personal health assistant that combines conversational health coaching, food image analysis, and interactive health analytics—all while keeping your data completely private.

Unlike cloud-based AI applications, **all AI processing runs locally on your machine** using **Ollama**, ensuring:

* 🔒 100% Privacy
* 🌐 No Internet Required
* 💰 No API Costs
* 💻 Runs Completely Offline

---

# ✨ Features

## 📊 Interactive Health Dashboard

* Live health metric cards
* Track:

  * 🚶 Steps
  * 😴 Sleep
  * ❤️ Resting Heart Rate
  * 😊 Mood
* Color-coded health status:

  * 🟢 Good
  * 🟡 Warning
  * 🔴 Concerning
* Week-over-week percentage change

---

## 📈 Trend Analysis

Visualize your health with interactive Plotly charts:

* Daily Steps (Goal Line Included)
* Sleep Duration (Target Line Included)
* Resting Heart Rate (Healthy Range Highlighted)

---

## 🔥 Correlation Heatmap

Discover relationships between your health metrics, such as:

* Sleep vs Mood
* Steps vs Heart Rate
* Sleep vs Activity

---

## 📝 Manual Health Logging

Log your daily health information using a simple, beginner-friendly interface.

Track:

* Steps
* Sleep Hours
* Resting Heart Rate
* Mood

No technical knowledge required.

---

## 🍎 AI Nutrition Log

### 📷 Food Image Analysis

Upload a meal photo and let the local **LLaVA Vision Model** estimate:

* Calories
* Protein
* Carbohydrates
* Fat

---

### ✍️ Text-Based Nutrition Analysis

Don't have an image?

Simply type what you ate and receive the same nutritional breakdown.

---

## 🤖 AI Health Coach

Chat with an AI assistant that understands your recent health history.

The assistant provides personalized guidance based on:

* Recent activity
* Sleep trends
* Nutrition logs
* Mood history

Powered locally using **Llama 3.2 via Ollama**.

---

## 🎨 Modern Custom UI

A premium Streamlit interface featuring:

* Glassmorphism design
* Gradient headings
* Smooth animations
* Custom CSS styling
* Fully responsive layout

---

# 🛠️ Tech Stack

| Layer                | Technology                 |
| -------------------- | -------------------------- |
| Programming Language | Python                     |
| UI Framework         | Streamlit                  |
| AI Models            | Ollama (Llama 3.2 & LLaVA) |
| Data Processing      | Pandas                     |
| Charts               | Plotly                     |
| Data Storage         | CSV & JSON (Local Storage) |

---

# 📦 Prerequisites

Before running the application, ensure you have:

* Python **3.10+**
* Ollama installed
* Ollama running locally
* Llama 3.2 model downloaded
* LLaVA vision model downloaded

---

# 🚀 Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

cd YOUR_REPO_NAME
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Download Required Ollama Models

```bash
ollama pull llama3.2

ollama pull llava
```

---

## 5️⃣ Start Ollama

```bash
ollama serve
```

Or simply open the Ollama desktop application.

---

## 6️⃣ Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser:

```
http://localhost:8501
```

---

# 📁 Project Structure

```
Cure-Sphere
│
├── app.py
├── requirements.txt
├── sample_health_data.csv
│
├── data
│   └── diet_logs.json
│
├── utils
│   ├── ai_helper.py
│   ├── data_analyzer.py
│   └── charts.py
│
└── .streamlit
    └── config.toml
```

---

# 📂 Project Overview

| File                     | Description                            |
| ------------------------ | -------------------------------------- |
| `app.py`                 | Main Streamlit application             |
| `requirements.txt`       | Python dependencies                    |
| `sample_health_data.csv` | Sample health dataset                  |
| `diet_logs.json`         | Stores nutrition history               |
| `ai_helper.py`           | Handles Ollama chat & image analysis   |
| `data_analyzer.py`       | Computes health metrics and statistics |
| `charts.py`              | Generates Plotly visualizations        |
| `config.toml`            | Streamlit configuration                |

---

# 🔒 Privacy

Cure Sphere is designed with privacy first.

* ✅ No Cloud Storage
* ✅ No External APIs
* ✅ No User Tracking
* ✅ No Internet Dependency
* ✅ Health Data Never Leaves Your Device

---

# ⚠️ Disclaimer

This application is intended for **educational and personal health tracking purposes only**.

It should **not** be considered a substitute for professional medical advice, diagnosis, or treatment.

Always consult a qualified healthcare professional regarding medical concerns.

---

# 📄 License

This project is open source and intended for **personal, educational, and learning purposes**.

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
