"""
Production RAG Engine for FitAI Pro AI Chatbot
Integrates Google Gemini API with RAG Vector Retrieval & Fallback Engine.
"""
import os
import logging
from config import Config
from chatbot.vector_store import vector_store
from recommendation.exercise_engine import exercise_engine
from recommendation.diet_engine import diet_engine
from recommendation.workout_engine import workout_engine
from models.exercise import ExerciseModel
import traceback
# Initialize Gemini API if configured
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False


def _query_gemini(prompt: str) -> str:
    api_key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "").strip()

    print("API Key Loaded:", bool(api_key))
    print("Gemini Available:", GEMINI_AVAILABLE)

    if not api_key or not GEMINI_AVAILABLE:
        return None

    try:
        genai.configure(api_key=api_key)

        print("Calling Gemini...")

        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)

        print("Gemini Response:", response)

        if hasattr(response, "text") and response.text:
            print("Gemini Success!")
            return response.text

    except Exception as e:
        print("\n" + "=" * 60)
        print("GEMINI ERROR")
        traceback.print_exc()
        print("=" * 60 + "\n")

    return None


def answer_query(user_query, user_profile=None):
    """
    RAG Chatbot pipeline:
    1. Retrieve relevant ExerciseDB records & South Indian meals context.
    2. Try Gemini API generation using retrieved RAG context.
    3. Fallback to intelligent local RAG response engine if Gemini API key is unset or unavailable.
    """
    q = user_query.strip()
    if not q:
        return "Please ask me a question about fitness, exercises, diet, or workout planning!"

    q_lower = q.lower()
    stats = vector_store.get_dataset_stats()

    # ── Step 1: Retrieve RAG Context ──────────────────────────────────────────
    matched_exercises = vector_store.search_exercises(q, top_k=3)
    matched_meals = vector_store.search_meals(q, top_k=3)
    print("Matched Meals:", matched_meals)
    print("Matched Exercises:", matched_exercises)

    rag_context_blocks = []
    if matched_exercises:
        ex_summary = []
        for raw_ex in matched_exercises:
            ex = ExerciseModel(raw_ex).to_dict()
            ex_summary.append(
                f"- Name: {ex['name']} | BodyPart: {ex['bodyPart']} | Target: {ex['target']} | "
                f"Equipment: {ex['equipment']} | Difficulty: {ex['difficulty']} | "
                f"MET: {ex['met']} | Calories/15m: ~{ex['caloriesBurned']} kcal | Instructions: {ex['instructions'][:200]}"
            )
        rag_context_blocks.append("RELEVANT EXERCISES FROM EXERCISEDB:\n" + "\n".join(ex_summary))

    if matched_meals:
        meal_summary = []
        for m in matched_meals:
            meal_summary.append(
                f"- Meal: {m.get('title')} | Type: {m.get('dish_type')} | Diet: {m.get('diet')} | "
                f"Calories: {m.get('calories_slot') or m.get('calories')} kcal | Protein: {m.get('protein_slot') or m.get('protein')}g | "
                f"Ingredients: {m.get('ingredients')}"
            )
        rag_context_blocks.append("RELEVANT SOUTH INDIAN MEALS FROM DATASET:\n" + "\n".join(meal_summary))

    context_str = "\n\n".join(rag_context_blocks) if rag_context_blocks else "No direct database match."

    # ── Step 2: Attempt Gemini API RAG Generation ─────────────────────────────
    gemini_prompt = (
        f"You are FitAI Pro, an expert AI Personal Fitness & Nutrition Coach.\n"
        f"Answer the user's question clearly, concisely, and professionally using markdown formatting.\n"
        f"If context is provided below from the ExerciseDB or South Indian Regional Meals dataset, incorporate it into your answer.\n\n"
        f"--- DATASET CONTEXT ---\n{context_str}\n---------------------\n\n"
        f"USER QUESTION: {q}\n\n"
        f"RESPONSE:"
    )

    gemini_response = _query_gemini(gemini_prompt)
    if gemini_response:
        return gemini_response

    # ── Step 3: Local RAG Fallback Engine ─────────────────────────────────────
    # 1. Dataset & Metadata Queries
    if any(k in q_lower for k in ['how many exercises', 'total exercises', 'exercise count']):
        return f"FitAI Pro is powered by the full **ExerciseDB Dataset featuring {stats['total_exercises']} exercises** across {len(stats['body_parts'])} body parts ({', '.join(stats['body_parts'][:7])})."

    if any(k in q_lower for k in ['muscle group', 'target muscle', 'muscles exist']):
        return f"The available **target muscle groups** in our dataset include:\n\n- " + "\n- ".join(stats['target_muscles'][:15])

    if any(k in q_lower for k in ['body part', 'bodyparts']):
        return f"The available **body parts** in FitAI Pro are:\n\n- " + "\n- ".join(stats['body_parts'])

    if any(k in q_lower for k in ['equipment']):
        return f"The **equipment types** supported in our exercise dataset are:\n\n- " + "\n- ".join(stats['equipments'])

    if any(k in q_lower for k in ['categories', 'exercise category']):
        return f"The **exercise categories** available in FitAI Pro are:\n\n- " + "\n- ".join(stats['categories'])

    if any(k in q_lower for k in ['explain this dataset', 'explain dataset', 'dataset fields', 'what are the fields']):
        return (
            f"### 📊 FitAI Pro Production Datasets Overview\n\n"
            f"1. **ExerciseDB Dataset ({stats['total_exercises']} Exercises)**\n"
            f"   - **Fields**: `{', '.join(stats['exercise_fields'])}`\n"
            f"   - Features real Exercise GIFs, MET-calculated calories burned, and automatic difficulty classification.\n\n"
            f"2. **South Indian Meals Dataset ({stats['total_south_indian_meals']} Regional Dishes)**\n"
            f"   - **Fields**: `{', '.join(stats['meal_fields'])}`\n"
            f"   - Features regional dishes with verified nutritional breakdown (Calories, Protein, Carbs, Fat, Sodium, Portions)."
        )

    # 2. Specific Exercise Retrieval & MET Calorie Calculation
    if any(k in q_lower for k in ['bench press', 'push up', 'squat', 'deadlift', 'pull up', 'curl', 'lunge', 'plank']):
        matches = vector_store.search_exercises(q, top_k=2)
        if matches:
            res = []
            for raw_ex in matches:
                ex_obj = ExerciseModel(raw_ex)
                ex = ex_obj.to_dict()
                res.append(
                    f"### 🏋️ {ex['name']}\n\n"
                    f"- **Body Part**: {ex['bodyPart'].title()}\n"
                    f"- **Target Muscle**: {ex['target'].title()}\n"
                    f"- **Secondary Muscles**: {ex['secondaryMuscles'] or 'Core'}\n"
                    f"- **Equipment**: {ex['equipment'].title()}\n"
                    f"- **Calculated Difficulty**: {ex['difficulty']}\n"
                    f"- **Calculated Calories Burned**: **~{ex['caloriesBurned']} kcal** / 15m (MET: {ex['met']})\n"
                    f"- **Exercise GIF**: ![Animation]({ex['gifUrl']})\n\n"
                    f"**Instructions**:\n{ex['instructions']}"
                )
            return "\n\n---\n\n".join(res)

    # 3. Search by muscle or equipment query
    if any(k in q_lower for k in ['chest', 'bicep', 'tricep', 'leg', 'back', 'shoulder', 'abs', 'dumbbell', 'barbell', 'without equipment', 'beginner exercise', 'burns more calories']):
        matches = vector_store.search_exercises(q, top_k=3)
        if matches:
            res = [f"Here are top matching exercises from our **870+ ExerciseDB dataset** for **'{q}'**:\n"]
            for raw_ex in matches:
                ex_obj = ExerciseModel(raw_ex)
                ex = ex_obj.to_dict()
                res.append(
                    f"#### 🏋️ {ex['name']}\n"
                    f"- **Body Part**: {ex['bodyPart'].title()} | **Target**: {ex['target'].title()}\n"
                    f"- **Equipment**: {ex['equipment'].title()} | **Difficulty**: {ex['difficulty']}\n"
                    f"- **Est. Burn (MET {ex['met']})**: ~{ex['caloriesBurned']} kcal/15m\n"
                    f"- **Instructions**: {ex['instructions'][:180]}...\n"
                )
            return "\n".join(res)

    # 4. South Indian Meals Queries
    if any(k in q_lower for k in ['dosa', 'idli', 'high protein', 'weight loss diet', 'muscle gain meal', 'south indian', 'vegetarian diet', 'calories in']):
        meals = vector_store.search_meals(q, top_k=3)
        if meals:
            res = [f"Here are regional South Indian food recommendations for **'{q}'**:\n"]
            for m in meals:
                res.append(
                    f"🍲 **{m.get('title')}** ({m.get('diet', '').title()})\n"
                    f"- **Meal Time**: {m.get('meal_time', '').title()} | **Type**: {m.get('dish_type', '').title()}\n"
                    f"- **Calories**: {m.get('calories_slot') or m.get('calories')} kcal\n"
                    f"- **Protein**: {m.get('protein_slot') or m.get('protein')}g | **Carbs**: {m.get('carbs_slot') or m.get('carbs')}g | **Fat**: {m.get('fat_slot') or m.get('fat')}g\n"
                    f"- **Ingredients**: {m.get('ingredients')}\n"
                )
            return "\n".join(res)

    # 5. Fitness Science & Concepts
    if 'what is bmi' in q_lower:
        return "**BMI (Body Mass Index)** is measured as weight (kg) / height² (m²). Standard categories: Underweight (<18.5), Normal (18.5–24.9), Overweight (25–29.9), Obese (≥30)."

    if 'what is bmr' in q_lower:
        return "**BMR (Basal Metabolic Rate)** is calculated using the Mifflin-St Jeor equation: Male `(10*W + 6.25*H - 5*A + 5)`, Female `(10*W + 6.25*H - 5*A - 161)`."

    # 6. Generators
    if any(k in q_lower for k in ['create my workout', 'build my workout', 'weekly workout', 'monthly workout', 'home workout']):
        plan = workout_engine.generate_routine(plan_type='7-Day Workout', goal='Gain Muscle', split='Push Pull Legs')
        res = [f"### 📋 {plan['plan_name']}\n", f"**Warm-up**: {plan['warmup']}\n"]
        for d in plan['days']:
            if d['routine']:
                ex_names = ", ".join([e['name'] for e in d['routine']])
                res.append(f"- **{d['day']}**: {ex_names}")
            else:
                res.append(f"- **{d['day']}**")
        return "\n".join(res)

    if any(k in q_lower for k in ['build my diet', 'create my diet', 'diet plan']):
        diet = diet_engine.generate_plan(target_calories=2000.0)
        return (
            f"### 🥗 Personalized South Indian Regional Diet Plan\n\n"
            f"- **Breakfast**: {diet['breakfast']['title']} ({diet['breakfast']['calories_num']} kcal, {diet['breakfast']['protein_num']}g protein)\n"
            f"- **Lunch**: {diet['lunch']['title']} ({diet['lunch']['calories_num']} kcal, {diet['lunch']['protein_num']}g protein)\n"
            f"- **Snack**: {diet['snack']['title']} ({diet['snack']['calories_num']} kcal)\n"
            f"- **Dinner**: {diet['dinner']['title']} ({diet['dinner']['calories_num']} kcal)\n\n"
            f"**Daily Totals**:\n"
            f"- ⚡ **Calories**: ~{diet['total_calories']} kcal\n"
            f"- 🥩 **Protein**: ~{diet['total_protein']}g"
        )

    # 7. Fallback Vector Match
    rel_ex = vector_store.search_exercises(q, top_k=2)
    rel_meals = vector_store.search_meals(q, top_k=2)

    if rel_ex or rel_meals:
        parts = ["Here is what I found in the FitAI Pro dataset:\n"]
        if rel_ex:
            parts.append("**Matching Exercises**:")
            for raw in rel_ex:
                e = ExerciseModel(raw).to_dict()
                parts.append(f"- **{e['name']}** ({e['bodyPart'].title()}): {e['instructions'][:150]}...")
        if rel_meals:
            parts.append("\n**Matching South Indian Dishes**:")
            for m in rel_meals:
                parts.append(f"- **{m.get('title')}**: {m.get('calories_slot') or m.get('calories')} kcal, {m.get('protein_slot') or m.get('protein')}g protein.")
        return "\n".join(parts)

    return (
        "I am **FitAI Pro**, your AI Personal Fitness Coach powered by **870+ ExerciseDB records** and **190 South Indian Meals**. "
        "Try asking me about exercises (*Bench Press*, *Push-up*), South Indian dishes (*Egg Dosa*, *Adai*), dataset stats, or ask me to build a custom workout or diet plan!"
    )
