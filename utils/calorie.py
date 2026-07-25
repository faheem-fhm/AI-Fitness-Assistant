"""
Calorie Target and Macronutrient Breakdown Utility
"""
from utils.bmr import calculate_bmr, calculate_tdee

def calculate_daily_targets(weight_kg, height_cm, age, gender='male', goal='Stay Fit', activity_level='moderate'):
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    goal_str = str(goal).lower()
    
    if 'lose' in goal_str or 'fat' in goal_str or 'weight loss' in goal_str:
        target_calories = tdee - 500.0  # 500 kcal deficit
        protein_per_kg = 2.0  # Higher protein for fat loss muscle retention
        fat_pct = 0.25
    elif 'gain' in goal_str or 'muscle' in goal_str or 'hypertrophy' in goal_str:
        target_calories = tdee + 400.0  # 400 kcal surplus
        protein_per_kg = 2.2
        fat_pct = 0.25
    elif 'flexibility' in goal_str or 'rehabilitation' in goal_str:
        target_calories = tdee
        protein_per_kg = 1.6
        fat_pct = 0.28
    else:  # Stay Fit / Maintenance / Cardio
        target_calories = tdee
        protein_per_kg = 1.8
        fat_pct = 0.25
    
    target_calories = max(target_calories, 1200.0)
    
    protein_g = round(float(weight_kg) * protein_per_kg, 1) if weight_kg else 120.0
    protein_calories = protein_g * 4.0
    
    fat_calories = target_calories * fat_pct
    fat_g = round(fat_calories / 9.0, 1)
    
    carb_calories = max(target_calories - (protein_calories + fat_calories), 0.0)
    carbs_g = round(carb_calories / 4.0, 1)
    
    # Water intake recommendation: ~35ml per kg body weight + 500ml
    water_liters = round((float(weight_kg or 70) * 0.035) + 0.5, 1)
    
    return {
        'bmr': bmr,
        'tdee': tdee,
        'target_calories': round(target_calories, 1),
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fat_g': fat_g,
        'water_liters': water_liters
    }
