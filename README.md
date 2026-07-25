# FitAI Pro – AI Personal Fitness Coach ⚡

> **Tagline**: AI-powered Exercise Recommendation, Regional Tamil Nadu Diet Planning & Intelligent Fitness Assistant

FitAI Pro is a production-level AI Personal Fitness Coach platform built with Flask, Python, SQLite, Jinja2, Chart.js, and an in-memory RAG Vector Retrieval engine.

---

## Key Features

### 1. Landing Page & Dashboard
- Modern dark-mode glassmorphic interface with vibrant neon accents.
- Live statistics banner (Curated exercises, 190 Tamil Nadu regional meals).
- Interactive BMI & Calorie calculator modal widget.
- Responsive layout across desktop, tablet, and mobile.

### 2. AI Exercise Recommender & Catalog
- Custom recommendations based on age, height, weight, gender, and fitness goal (*Gain Muscle, Lose Fat, Stay Fit, Improve Flexibility, Cardio, Rehabilitation*).
- Interactive filter bar by **Body Part**, **Equipment**, **Difficulty**, and **Target Muscle**.
- Exercise detail pages featuring GIF/images, step-by-step instructions, secondary muscle highlights, common mistakes to avoid, and embedded YouTube video tutorials.

### 3. AI Tamil Nadu Regional Diet Planner
- Integrated with authentic **Tamil Nadu Meals Dataset** (`190 dishes`).
- Generates regional meal recommendations (*Egg Dosa, Adai, Pongal, Sambar, Chettinad Curries, Sundal, Poriyal*) matching target calories, protein, carbs, and fat macros.

### 4. AI Workout Routine Planner
- Generates **7-Day** and **30-Day** structured plans.
- Supports **Home Workouts (Bodyweight)** vs **Gym Workouts**.
- Supports **Push Pull Legs**, **Bro Split**, **Beginner**, and **Advanced** routines.
- Includes dynamic warm-up drills, cool-down mobility, and coach safety guidelines.

### 5. RAG AI Chatbot Assistant
- Integrated RAG Vector Store engine (`vector_store.py`, `embeddings.py`, `rag.py`).
- Answers questions about exercises (*"What is Bench Press?"*, *"Dumbbell chest exercises"*), dataset metadata (*"How many exercises exist?"*, *"What muscle groups are included?"*), Tamil Nadu foods (*"Calories in dosa"*), and fitness science (*BMI, BMR, TDEE, protein intake*).

### 6. Dashboard Analytics & Progress Tracking
- Interactive Chart.js graphs for **Weight Timeline**, **Macro Breakdown Pie Chart**, and **Workout Completion History**.

### 7. Authentication, Profiles & Gamification
- User Login, Signup, Profile updates, BMI recalculations.
- Workout streak counters and gamification badges (*5-Day Streak, First Workout, Tamil Nadu Gourmet*).

### 8. Admin Panel
- Comprehensive overview of registered users, exercise statistics, and user feedback logs.

---

## Folder Structure

```
FitAI-Pro/
│
├── app.py
├── config.py
├── requirements.txt
│
├── model/
│
├── chatbot/
│   ├── rag.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── prompt.py
│
├── dataset/
│   ├── exercises.csv
│   └── tamil_nadu_meals.csv
│
├── utils/
│   ├── bmi.py
│   ├── bmr.py
│   ├── calorie.py
│   └── recommender.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── exercises.html
│   ├── exercise_detail.html
│   ├── diet_planner.html
│   ├── workout_planner.html
│   ├── chatbot.html
│   ├── analytics.html
│   ├── profile.html
│   ├── admin.html
│   ├── login.html
│   └── register.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       ├── charts.js
│       └── chatbot.js
│
├── database/
│   └── fitai.db
└── README.md
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install flask jinja2 werkzeug
```

### 2. Launch Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

### Demo Logins
- **User Demo**: `user@fitai.pro` / `password123`
- **Admin Panel**: `admin@fitai.pro` / `admin123`
