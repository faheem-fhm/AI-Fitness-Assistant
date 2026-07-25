"""
AI Recommender Utility for Exercises, Tamil Nadu Regional Meal Plans, and Workout Routines
"""
import os
import csv
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXERCISES_PATH = os.path.join(BASE_DIR, 'dataset', 'exercises.csv')
MEALS_PATH = os.path.join(BASE_DIR, 'dataset', 'tamil_nadu_meals.csv')

def load_exercises():
    exercises = []
    if os.path.exists(EXERCISES_PATH):
        with open(EXERCISES_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                exercises.append(row)
    return exercises

def load_tamil_nadu_meals():
    meals = []
    if os.path.exists(MEALS_PATH):
        with open(MEALS_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ensure numerical conversion for calories & protein if present
                try:
                    row['calories_num'] = float(row.get('calories_slot') or row.get('calories') or 0)
                except Exception:
                    row['calories_num'] = 0.0
                try:
                    row['protein_num'] = float(row.get('protein_slot') or row.get('protein') or 0)
                except Exception:
                    row['protein_num'] = 0.0
                try:
                    row['carbs_num'] = float(row.get('carbs_slot') or row.get('carbs') or 0)
                except Exception:
                    row['carbs_num'] = 0.0
                try:
                    row['fat_num'] = float(row.get('fat_slot') or row.get('fat') or 0)
                except Exception:
                    row['fat_num'] = 0.0
                meals.append(row)
    return meals

def recommend_exercises(goal='Gain Muscle', difficulty='Beginner', body_part=None, equipment=None, count=6):
    all_ex = load_exercises()
    filtered = []
    
    goal_lower = goal.lower()
    diff_lower = difficulty.lower()
    
    for ex in all_ex:
        # Match body part
        if body_part and body_part.lower() != 'all':
            if body_part.lower() not in ex['bodyPart'].lower() and body_part.lower() not in ex['target'].lower():
                continue
        # Match equipment
        if equipment and equipment.lower() != 'all':
            if equipment.lower() not in ex['equipment'].lower():
                continue
        filtered.append(ex)

    if not filtered:
        filtered = all_ex

    # Assign recommended sets, reps, rest based on goal
    recommendations = []
    for ex in filtered[:count]:
        if 'muscle' in goal_lower or 'hypertrophy' in goal_lower:
            sets, reps, rest = '3-4', '8-12 reps', '60-90 sec'
        elif 'fat' in goal_lower or 'weight' in goal_lower or 'cardio' in goal_lower:
            sets, reps, rest = '3-4', '12-15 reps', '30-45 sec'
        elif 'strength' in goal_lower:
            sets, reps, rest = '4-5', '5 reps', '2-3 min'
        else: # Flexibility / Rehab
            sets, reps, rest = '3', '12-15 reps / hold 30s', '45 sec'
            
        ex_copy = dict(ex)
        ex_copy['recommended_sets'] = sets
        ex_copy['recommended_reps'] = reps
        ex_copy['recommended_rest'] = rest
        recommendations.append(ex_copy)
        
    return recommendations

def recommend_tamil_nadu_diet(target_calories=2000, diet_pref='any', goal='Stay Fit'):
    meals = load_tamil_nadu_meals()
    if not meals:
        return {}

    pref_lower = diet_pref.lower()
    if 'veg' in pref_lower and 'non' not in pref_lower:
        filtered_meals = [m for m in meals if 'non' not in m.get('diet', '').lower()]
    elif 'non' in pref_lower:
        filtered_meals = [m for m in meals if 'non' in m.get('diet', '').lower() or 'veg' in m.get('diet', '').lower()]
    else:
        filtered_meals = meals

    if not filtered_meals:
        filtered_meals = meals

    def get_by_slot(meal_time_key):
        items = [m for m in filtered_meals if meal_time_key in m.get('meal_time', '').lower()]
        return items if items else filtered_meals

    breakfast_opts = get_by_slot('breakfast')
    lunch_opts = get_by_slot('lunch')
    dinner_opts = get_by_slot('dinner')
    snack_opts = get_by_slot('snack') or get_by_slot('tiffin') or filtered_meals

    breakfast = random.choice(breakfast_opts)
    lunch = random.choice(lunch_opts)
    dinner = random.choice(dinner_opts)
    snack = random.choice(snack_opts)

    tot_cal = breakfast['calories_num'] + lunch['calories_num'] + dinner['calories_num'] + snack['calories_num']
    tot_protein = breakfast['protein_num'] + lunch['protein_num'] + dinner['protein_num'] + snack['protein_num']
    tot_carbs = breakfast['carbs_num'] + lunch['carbs_num'] + dinner['carbs_num'] + snack['carbs_num']
    tot_fat = breakfast['fat_num'] + lunch['fat_num'] + dinner['fat_num'] + snack['fat_num']

    return {
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'snack': snack,
        'total_calories': round(tot_cal, 1),
        'total_protein': round(tot_protein, 1),
        'total_carbs': round(tot_carbs, 1),
        'total_fat': round(tot_fat, 1),
        'water_intake_l': 3.5,
        'goal': goal
    }

def generate_workout_plan(plan_type='7-Day Workout', goal='Gain Muscle', location='Gym Workout', split='Push Pull Legs', level='Beginner'):
    exercises = load_exercises()
    
    def get_ex_by_bodypart(bp_list):
        return [e for e in exercises if any(b in e['bodyPart'].lower() for b in bp_list)]

    chest_ex = get_ex_by_bodypart(['chest']) or exercises[:3]
    back_ex = get_ex_by_bodypart(['back']) or exercises[3:6]
    leg_ex = get_ex_by_bodypart(['legs']) or exercises[6:9]
    shoulder_ex = get_ex_by_bodypart(['shoulders']) or exercises[9:12]
    arm_ex = get_ex_by_bodypart(['upper arms']) or exercises[12:15]
    core_ex = get_ex_by_bodypart(['waist', 'cardio']) or exercises[15:18]

    if split == 'Push Pull Legs':
        days = [
            {'day': 'Day 1: Push (Chest, Shoulders, Triceps)', 'routine': chest_ex[:2] + shoulder_ex[:1] + arm_ex[1:2]},
            {'day': 'Day 2: Pull (Back, Biceps, Rear Delts)', 'routine': back_ex[:3] + arm_ex[:1]},
            {'day': 'Day 3: Legs & Abs', 'routine': leg_ex[:3] + core_ex[:1]},
            {'day': 'Day 4: Active Recovery & Mobility', 'routine': [e for e in exercises if 'flexibility' in e['category'].lower() or 'cat-cow' in e['name'].lower()] or core_ex[:2]},
            {'day': 'Day 5: Push Focus', 'routine': chest_ex[1:3] + shoulder_ex[1:2]},
            {'day': 'Day 6: Pull & Legs Split', 'routine': back_ex[:2] + leg_ex[1:3]},
            {'day': 'Day 7: Full Rest & Hydration', 'routine': []}
        ]
    elif split == 'Bro Split':
        days = [
            {'day': 'Day 1: Chest Blast', 'routine': chest_ex[:4]},
            {'day': 'Day 2: Back & Lats', 'routine': back_ex[:4]},
            {'day': 'Day 3: Shoulder Sculpt', 'routine': shoulder_ex[:3] + core_ex[:1]},
            {'day': 'Day 4: Leg Day Strength', 'routine': leg_ex[:4]},
            {'day': 'Day 5: Arms (Biceps & Triceps)', 'routine': arm_ex[:4]},
            {'day': 'Day 6: Cardio & Abs Core', 'routine': core_ex[:3]},
            {'day': 'Day 7: Rest & Recovery', 'routine': []}
        ]
    else: # Upper/Lower or Beginner Full Body
        days = [
            {'day': 'Day 1: Full Body Strength A', 'routine': [chest_ex[0], back_ex[0], leg_ex[0], shoulder_ex[0]]},
            {'day': 'Day 2: Active Rest / Walk', 'routine': []},
            {'day': 'Day 3: Full Body Strength B', 'routine': [chest_ex[1], back_ex[1], leg_ex[1], arm_ex[0]]},
            {'day': 'Day 4: Rest', 'routine': []},
            {'day': 'Day 5: Full Body & Core', 'routine': [leg_ex[2], back_ex[2], shoulder_ex[1], core_ex[0]]},
            {'day': 'Day 6: Light Mobility & Cardio', 'routine': core_ex[1:3]},
            {'day': 'Day 7: Rest', 'routine': []}
        ]

    return {
        'plan_name': f'{level} {split} ({location}) - {goal}',
        'duration': plan_type,
        'warmup': '5-10 mins dynamic stretching (Arm circles, Leg swings, Torso twists)',
        'cooldown': '5-10 mins static stretching & foam rolling',
        'safety_tips': 'Maintain proper form, stay hydrated, track weight progression, avoid lifting beyond failure without a spotter.',
        'days': days
    }
