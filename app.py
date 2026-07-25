"""
FitAI Pro - Production Level Flask Server
Includes Modular Models, Recommendation Engines, Vector RAG Engine, Dynamic Planner Forms & Dynamic Calculator Engine.
"""
import os
import math
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from utils.bmi import calculate_bmi, get_bmi_category, get_ideal_weight_range
from utils.bmr import calculate_bmr, calculate_tdee
from utils.calorie import calculate_daily_targets
from utils.youtube_map import get_video_id, get_thumbnail_url, get_embed_url

from models.exercise import ExerciseModel, load_all_exercises
from models.user import UserModel
from models.workout import WorkoutLogModel

from recommendation.exercise_engine import exercise_engine
from recommendation.diet_engine import diet_engine
from recommendation.workout_engine import workout_engine

from chatbot.rag import answer_query
from chatbot.vector_store import vector_store


from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

app = Flask(__name__)
app.config.from_object(Config)
print("Gemini Loaded:", bool(Config.GEMINI_API_KEY))
print("API Key:", Config.GEMINI_API_KEY[:10] + "..." if Config.GEMINI_API_KEY else "Not Found")

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER DEFAULT 25,
            height REAL DEFAULT 175.0,
            weight REAL DEFAULT 70.0,
            gender TEXT DEFAULT 'male',
            goal TEXT DEFAULT 'Gain Muscle',
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER DEFAULT 3,
            reps INTEGER DEFAULT 10,
            weight_kg REAL DEFAULT 0.0,
            calories_burned REAL DEFAULT 100.0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        demo_pw = generate_password_hash("password123")
        admin_pw = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, age, height, weight, gender, goal, is_admin)
            VALUES ('Fitness Champ', 'user@fitai.pro', ?, 24, 175.0, 72.0, 'male', 'Gain Muscle', 0)
        """, (demo_pw,))
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, age, height, weight, gender, goal, is_admin)
            VALUES ('Admin Coach', 'admin@fitai.pro', ?, 30, 180.0, 80.0, 'male', 'Stay Fit', 1)
        """, (admin_pw,))
        conn.commit()

        cursor.execute("SELECT id FROM users WHERE email='user@fitai.pro'")
        user_row = cursor.fetchone()
        if user_row:
            uid = user_row['id']
            weights = [76.0, 75.2, 74.5, 73.8, 73.0, 72.0]
            for w in weights:
                cursor.execute("INSERT INTO weight_history (user_id, weight_kg) VALUES (?, ?)", (uid, w))
            
            cursor.execute("INSERT INTO workout_history (user_id, exercise_name, sets, reps, weight_kg, calories_burned) VALUES (?, 'Bench Press', 4, 10, 60.0, 120.0)", (uid,))
            cursor.execute("INSERT INTO workout_history (user_id, exercise_name, sets, reps, weight_kg, calories_burned) VALUES (?, 'Barbell Squat', 4, 8, 80.0, 150.0)", (uid,))
            conn.commit()

    conn.close()

with app.app_context():
    init_db()

    # Auto-migrate: safely add any columns that may be missing in older databases
    _conn = get_db()
    _cur = _conn.cursor()
    _cur.execute("PRAGMA table_info(workout_history)")
    _existing_cols = [row[1] for row in _cur.fetchall()]
    if 'calories_burned' not in _existing_cols:
        _cur.execute("ALTER TABLE workout_history ADD COLUMN calories_burned REAL DEFAULT 0.0")
        _conn.commit()
    _conn.close()

    vector_store.build_index()

@app.context_processor
def inject_user():
    user_obj = None
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row:
            user_obj = UserModel(row)
    return dict(current_user=user_obj)

# --- WEB UI ROUTES ---

@app.route('/')
def index():
    all_ex = load_all_exercises()
    meals = diet_engine.meals

    # Real counts from DB — no fake numbers
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT email) FROM users")
    real_user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM workout_history")
    real_workout_count = cursor.fetchone()[0]
    conn.close()

    stats = {
        'total_exercises': len(all_ex),
        'total_meals': len(meals),
        'total_users': real_user_count,
        'workouts_completed': real_workout_count
    }
    return render_template('index.html', stats=stats, popular_exercises=all_ex[:6])

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user_row = cursor.fetchone()
    user = UserModel(user_row)

    cursor.execute("SELECT * FROM weight_history WHERE user_id = ? ORDER BY recorded_at ASC", (session['user_id'],))
    weight_logs = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM workout_history WHERE user_id = ?", (session['user_id'],))
    completed_workouts_cnt = cursor.fetchone()[0]

    conn.close()

    bmi = user.get_bmi()
    bmi_info = user.get_bmi_info()
    targets = user.get_daily_targets()

    rec_ex = exercise_engine.recommend(goal=user.goal, user_weight_kg=user.weight, limit=4)
    rec_diet = diet_engine.generate_plan(target_calories=targets['target_calories'], goal=user.goal)

    ai_motivation = f"🔥 Keep grinding, {user.username}! You are on track for {user.goal}. Hydrate with {targets['water_liters']}L water today!"
    ai_weekly_report = {
        'weight_change': round(weight_logs[-1]['weight_kg'] - weight_logs[0]['weight_kg'], 1) if len(weight_logs) > 1 else 0.0,
        'calories_burned_week': completed_workouts_cnt * 135,
        'completion_rate': min(100, int((completed_workouts_cnt / 12) * 100)) if completed_workouts_cnt else 45
    }

    return render_template(
        'dashboard.html',
        user=user,
        bmi=bmi,
        bmi_info=bmi_info,
        targets=targets,
        rec_ex=rec_ex,
        rec_diet=rec_diet,
        weight_logs=weight_logs,
        completed_workouts_cnt=completed_workouts_cnt,
        ai_motivation=ai_motivation,
        ai_weekly_report=ai_weekly_report
    )

@app.route('/exercises')
def exercises():
    page = int(request.args.get('page', 1))
    per_page = 12
    body_part = request.args.get('body_part', 'all')
    equipment = request.args.get('equipment', 'all')
    difficulty = request.args.get('difficulty', 'all')
    sort_by = request.args.get('sort', 'name')
    search_q = request.args.get('q', '').strip()

    user_weight = 70.0
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT weight FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row: user_weight = row['weight']

    all_ex = load_all_exercises(user_weight)
    filtered = []

    for ex in all_ex:
        if body_part != 'all' and body_part.lower() not in ex['bodyPart'].lower():
            continue
        if equipment != 'all' and equipment.lower() not in ex['equipment'].lower():
            continue
        if difficulty != 'all' and difficulty.lower() != ex['difficulty'].lower():
            continue
        if search_q:
            blob = f"{ex['name']} {ex['bodyPart']} {ex['target']} {ex['equipment']} {ex['instructions']}".lower()
            if search_q.lower() not in blob:
                continue
        filtered.append(ex)

    if sort_by == 'calories':
        filtered.sort(key=lambda x: x['caloriesBurned'], reverse=True)
    elif sort_by == 'name_desc':
        filtered.sort(key=lambda x: x['name'], reverse=True)
    else:
        filtered.sort(key=lambda x: x['name'])

    total_items = len(filtered)
    total_pages = math.ceil(total_items / per_page) or 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_exercises = filtered[start_idx:end_idx]

    stats = vector_store.get_dataset_stats()
    return render_template(
        'exercises.html',
        exercises=paginated_exercises,
        stats=stats,
        current_bp=body_part,
        current_eq=equipment,
        current_diff=difficulty,
        sort_by=sort_by,
        search_q=search_q,
        page=page,
        total_pages=total_pages,
        total_items=total_items
    )

@app.route('/exercise/<ex_id>')
def exercise_detail(ex_id):
    user_weight = 70.0
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT weight FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row: user_weight = row['weight']

    all_ex = load_all_exercises(user_weight)
    exercise = next((e for e in all_ex if str(e['id']) == str(ex_id)), None)
    if not exercise:
        flash('Exercise not found', 'danger')
        return redirect(url_for('exercises'))

    related = [e for e in all_ex if e['bodyPart'] == exercise['bodyPart'] and str(e['id']) != str(ex_id)][:3]

    # Curated YouTube video for this exercise
    vid_id    = get_video_id(exercise['name'], exercise.get('bodyPart'))
    vid_thumb = get_thumbnail_url(vid_id)
    vid_embed = get_embed_url(vid_id)

    ai_explanation = (
        f"{exercise['name']} is a {exercise['difficulty']} level {exercise['category']} "
        f"exercise targeting the {exercise['target'].title()}. "
        f"Using MET {exercise['met']}, a 70 kg person burns ~{exercise['caloriesBurned']} kcal "
        f"per 15-min set. Focus on controlled eccentric (lowering) phase for maximum muscle activation."
    )

    return render_template('exercise_detail.html',
        exercise=exercise, related=related,
        ai_explanation=ai_explanation,
        vid_id=vid_id, vid_thumb=vid_thumb, vid_embed=vid_embed)

@app.route('/diet-planner', methods=['GET', 'POST'])
def diet_planner():
    user_weight = 70.0
    user_height = 175.0
    user_age = 25
    user_gender = 'male'
    user_goal = 'Gain Muscle'

    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row:
            user_weight, user_height, user_age = row['weight'], row['height'], row['age']
            user_gender, user_goal = row['gender'], row['goal']

    targets = calculate_daily_targets(user_weight, user_height, user_age, user_gender, user_goal)

    req_cal = request.args.get('calories') or request.form.get('calories')
    target_cal = float(req_cal) if req_cal else targets['target_calories']
    diet_pref = request.args.get('diet_pref') or request.form.get('diet_pref') or 'any'
    goal = request.args.get('goal') or request.form.get('goal') or user_goal

    diet_plan = diet_engine.generate_plan(target_calories=target_cal, diet_pref=diet_pref, goal=goal)

    ai_meal_summary = (
        f"🥗 **AI Meal Summary**: Designed for **{goal}** ({diet_pref.replace('_', ' ').title()}) with {diet_plan['total_calories']} kcal and {diet_plan['total_protein']}g protein. "
        f"Features regional South Indian foods providing optimal complex carbs and lean protein."
    )

    return render_template(
        'diet_planner.html',
        targets=targets,
        diet_plan=diet_plan,
        ai_meal_summary=ai_meal_summary,
        current_calories=target_cal,
        current_pref=diet_pref,
        current_goal=goal
    )

@app.route('/workout-planner', methods=['GET', 'POST'])
def workout_planner():
    user_goal = 'Gain Muscle'
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT goal FROM users WHERE id = ?", (session['user_id'],))
        row = cursor.fetchone()
        conn.close()
        if row: user_goal = row['goal']

    plan_type = request.args.get('plan_type') or request.form.get('plan_type') or '7-Day Workout'
    location = request.args.get('location') or request.form.get('location') or 'Gym Workout'
    split = request.args.get('split') or request.form.get('split') or 'Push Pull Legs'
    level = request.args.get('level') or request.form.get('level') or 'Beginner'

    plan = workout_engine.generate_routine(plan_type=plan_type, goal=user_goal, location=location, split=split, level=level)
    return render_template(
        'workout_planner.html',
        plan=plan,
        current_plan_type=plan_type,
        current_location=location,
        current_split=split,
        current_level=level
    )

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user_row = cursor.fetchone()
    user = UserModel(user_row)

    cursor.execute("SELECT * FROM weight_history WHERE user_id = ? ORDER BY recorded_at ASC", (session['user_id'],))
    weight_logs = cursor.fetchall()

    cursor.execute("SELECT * FROM workout_history WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 20", (session['user_id'],))
    workout_logs = cursor.fetchall()

    # ── Live Progress Metrics ────────────────────────────────────────────────
    weight_values = [w['weight_kg'] for w in weight_logs]
    weight_change = round(weight_values[-1] - weight_values[0], 1) if len(weight_values) > 1 else 0.0
    weight_trend  = 'down' if weight_change < 0 else ('up' if weight_change > 0 else 'same')

    total_cals_burned = sum(w['calories_burned'] for w in workout_logs if w['calories_burned'])
    total_workouts    = len(workout_logs)

    # Workout streak: count consecutive days from today backward
    from datetime import datetime, timedelta
    streak = 0
    if workout_logs:
        logged_dates = set()
        for w in workout_logs:
            try: logged_dates.add(w['recorded_at'][:10])
            except: pass
        check_day = datetime.now().date()
        for _ in range(60):
            if str(check_day) in logged_dates:
                streak += 1
                check_day -= timedelta(days=1)
            else:
                break

    conn.close()

    bmi = user.get_bmi()
    bmi_info = user.get_bmi_info()
    targets = user.get_daily_targets()

    progress = {
        'weight_change': weight_change,
        'weight_trend': weight_trend,
        'total_cals_burned': round(total_cals_burned, 1),
        'total_workouts': total_workouts,
        'streak': streak,
        'current_weight': weight_values[-1] if weight_values else user.weight,
        'start_weight': weight_values[0] if weight_values else user.weight,
    }

    direction = 'losing weight' if weight_trend == 'down' else ('gaining weight' if weight_trend == 'up' else 'maintaining weight')
    ai_progress_forecast = (
        f"You are currently {direction} ({abs(weight_change)} kg change). "
        f"With {total_workouts} sessions logged burning {round(total_cals_burned)} kcal total, "
        f"keep your daily target of {targets['target_calories']} kcal to reach your {user.goal} goal."
    )

    return render_template(
        'analytics.html',
        user=user,
        bmi=bmi,
        bmi_info=bmi_info,
        targets=targets,
        weight_logs=weight_logs,
        workout_logs=workout_logs,
        progress=progress,
        ai_progress_forecast=ai_progress_forecast
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        age = int(request.form.get('age', 25))
        height = float(request.form.get('height', 175.0))
        weight = float(request.form.get('weight', 70.0))
        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'Gain Muscle')

        cursor.execute("""
            UPDATE users SET age = ?, height = ?, weight = ?, gender = ?, goal = ? WHERE id = ?
        """, (age, height, weight, gender, goal, session['user_id']))

        cursor.execute("INSERT INTO weight_history (user_id, weight_kg) VALUES (?, ?)", (session['user_id'], weight))
        conn.commit()
        flash('Profile & Body Metrics Updated Successfully!', 'success')

    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user_row = cursor.fetchone()
    user = UserModel(user_row)
    conn.close()

    return render_template('profile.html', user=user, bmi=user.get_bmi(), bmi_info=user.get_bmi_info())

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user_row = cursor.fetchone()

    if not user_row or not user_row['is_admin']:
        flash('Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    all_users = cursor.fetchall()
    conn.close()

    stats = vector_store.get_dataset_stats()
    return render_template('admin.html', user=user_row, all_users=all_users, stats=stats)

# --- AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        age = int(request.form.get('age', 25))
        height = float(request.form.get('height', 175.0))
        weight = float(request.form.get('weight', 70.0))
        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'Gain Muscle')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('login'))

        pw_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, age, height, weight, gender, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, pw_hash, age, height, weight, gender, goal))
        new_id = cursor.lastrowid
        cursor.execute("INSERT INTO weight_history (user_id, weight_kg) VALUES (?, ?)", (new_id, weight))
        conn.commit()
        conn.close()

        session['user_id'] = new_id
        session['username'] = username
        flash("Registration successful! Welcome to FitAI Pro.", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/log-workout', methods=['POST'])
def log_workout():
    if 'user_id' not in session:
        flash('Please login to log workouts.', 'warning')
        return redirect(url_for('login'))

    exercise_name = request.form.get('exercise_name', 'Unknown Exercise')
    exercise_id   = request.form.get('exercise_id', '')
    sets          = int(request.form.get('sets', 3))
    reps          = int(request.form.get('reps', 10))
    weight_kg     = float(request.form.get('weight_kg', 0.0))

    # Fetch user weight for calorie calculation
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT weight FROM users WHERE id = ?", (session['user_id'],))
    row = cursor.fetchone()
    user_weight = row['weight'] if row else 70.0

    # Estimate calories: sets × reps × 0.5 kcal (rough avg), boosted by user weight ratio
    calories_burned = round(sets * reps * 0.5 * (user_weight / 70.0), 1)

    cursor.execute("""
        INSERT INTO workout_history (user_id, exercise_name, sets, reps, weight_kg, calories_burned)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session['user_id'], exercise_name, sets, reps, weight_kg, calories_burned))
    conn.commit()
    conn.close()

    flash(f"✅ '{exercise_name}' logged to your workout history!", 'success')
    if exercise_id:
        return redirect(url_for('exercise_detail', ex_id=exercise_id))
    return redirect(url_for('analytics'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# --- FULL PRODUCTION REST API SUITE ---


@app.route('/api/calculate-bmi-bmr', methods=['POST'])
@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    data = request.get_json() or {}
    weight = float(data.get('weight', 70.0))
    height = float(data.get('height', 175.0))
    age = int(data.get('age', 25))
    gender = data.get('gender', 'male')
    goal = data.get('goal', 'Gain Muscle')

    bmi = calculate_bmi(weight, height)
    bmi_info = get_bmi_category(bmi)
    ideal_range = get_ideal_weight_range(height)
    targets = calculate_daily_targets(weight, height, age, gender, goal)

    return jsonify({
        'status': 'success',
        'bmi': bmi,
        'category': bmi_info['category'],
        'color': bmi_info['color'],
        'advice': bmi_info['advice'],
        'ideal_min': ideal_range[0],
        'ideal_max': ideal_range[1],
        'targets': targets
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message is empty'}), 400
    response_text = answer_query(user_message)
    return jsonify({'status': 'success', 'response': response_text})

@app.route('/api/workout', methods=['POST'])
def api_workout():
    data = request.get_json() or {}
    plan_type = data.get('plan_type', '7-Day Workout')
    goal = data.get('goal', 'Gain Muscle')
    location = data.get('location', 'Gym Workout')
    split = data.get('split', 'Push Pull Legs')
    level = data.get('level', 'Beginner')
    plan = workout_engine.generate_routine(plan_type=plan_type, goal=goal, location=location, split=split, level=level)
    return jsonify({'status': 'success', 'workout_plan': plan})

@app.route('/api/diet', methods=['POST'])
def api_diet():
    data = request.get_json() or {}
    target_cal = float(data.get('calories', 2000.0))
    diet_pref = data.get('diet_pref', 'any')
    goal = data.get('goal', 'Gain Muscle')
    plan = diet_engine.generate_plan(target_calories=target_cal, diet_pref=diet_pref, goal=goal)
    return jsonify({'status': 'success', 'diet_plan': plan})

@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.get_json() or {}
        weight = float(data.get('weight', 70.0))
        height = float(data.get('height', 175.0))
        age = int(data.get('age', 25))
        goal = data.get('goal', 'Gain Muscle')
        cursor.execute("UPDATE users SET weight = ?, height = ?, age = ?, goal = ? WHERE id = ?", (weight, height, age, goal, session['user_id']))
        cursor.execute("INSERT INTO weight_history (user_id, weight_kg) VALUES (?, ?)", (session['user_id'], weight))
        conn.commit()

    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    row = cursor.fetchone()
    conn.close()
    user = UserModel(row)
    return jsonify({
        'status': 'success',
        'username': user.username,
        'email': user.email,
        'weight': user.weight,
        'height': user.height,
        'bmi': user.get_bmi(),
        'daily_targets': user.get_daily_targets()
    })

@app.route('/api/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '').strip()
    bp = request.args.get('body_part', 'all')
    eq = request.args.get('equipment', 'all')

    all_ex = load_all_exercises()
    results = []
    for ex in all_ex:
        if bp != 'all' and bp.lower() not in ex['bodyPart'].lower(): continue
        if eq != 'all' and eq.lower() not in ex['equipment'].lower(): continue
        if q:
            blob = f"{ex['name']} {ex['bodyPart']} {ex['target']} {ex['equipment']}".lower()
            if q.lower() not in blob: continue
        results.append(ex)

    return jsonify({
        'status': 'success',
        'total_results': len(results),
        'results': results[:20]
    })

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json() or {}
    goal = data.get('goal', 'Gain Muscle')
    bp = data.get('body_part', 'all')
    eq = data.get('equipment', 'all')
    weight = float(data.get('weight_kg', 70.0))
    recs = exercise_engine.recommend(goal=goal, body_part=bp, equipment=eq, user_weight_kg=weight, limit=6)
    return jsonify({'status': 'success', 'recommendations': recs})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'status': 'success', 'message': f'Logged in as {user["username"]}'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    age = int(data.get('age', 25))
    height = float(data.get('height', 175.0))
    weight = float(data.get('weight', 70.0))
    gender = data.get('gender', 'male')
    goal = data.get('goal', 'Gain Muscle')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': 'Email already exists'}), 400

    pw_hash = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, age, height, weight, gender, goal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, email, pw_hash, age, height, weight, gender, goal))
    new_id = cursor.lastrowid
    cursor.execute("INSERT INTO weight_history (user_id, weight_kg) VALUES (?, ?)", (new_id, weight))
    conn.commit()
    conn.close()

    session['user_id'] = new_id
    session['username'] = username
    return jsonify({'status': 'success', 'message': 'Account created successfully'})


if __name__ == '__main__':
    print("FitAI Pro server running on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
