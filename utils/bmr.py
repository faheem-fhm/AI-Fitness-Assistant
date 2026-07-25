"""
BMR and TDEE Calculator Utility using Mifflin-St Jeor Equation
"""

def calculate_bmr(weight_kg, height_cm, age, gender='male'):
    """
    Mifflin-St Jeor Equation:
    Male: BMR = (10 x weight in kg) + (6.25 x height in cm) - (5 x age in years) + 5
    Female: BMR = (10 x weight in kg) + (6.25 x height in cm) - (5 x age in years) - 161
    """
    if not weight_kg or not height_cm or not age:
        return 0.0
    
    base = (10.0 * float(weight_kg)) + (6.25 * float(height_cm)) - (5.0 * float(age))
    if str(gender).lower() in ['female', 'f', 'woman']:
        bmr = base - 161.0
    else:
        bmr = base + 5.0
    return round(max(bmr, 800.0), 1)

def calculate_tdee(bmr, activity_level='moderate'):
    multipliers = {
        'sedentary': 1.2,      # Little or no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Hard exercise 6-7 days/week
        'very_active': 1.9     # Very hard exercise & physical job
    }
    mult = multipliers.get(str(activity_level).lower(), 1.55)
    return round(bmr * mult, 1)
