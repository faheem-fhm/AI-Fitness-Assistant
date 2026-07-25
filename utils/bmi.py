"""
BMI Calculator Utility
"""

def calculate_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm or height_cm <= 0:
        return 0.0
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return {
            'category': 'Underweight',
            'color': '#3b82f6', # blue
            'advice': 'Consider increasing nutrient-rich calorie intake with protein and complex carbs.'
        }
    elif 18.5 <= bmi < 24.9:
        return {
            'category': 'Normal Weight',
            'color': '#10b981', # green
            'advice': 'Great job! Maintain your current balanced lifestyle and activity level.'
        }
    elif 25.0 <= bmi < 29.9:
        return {
            'category': 'Overweight',
            'color': '#f59e0b', # amber
            'advice': 'Incorporate consistent cardio, strength training, and a slight calorie deficit.'
        }
    else:
        return {
            'category': 'Obese',
            'color': '#ef4444', # red
            'advice': 'Consult a fitness coach or dietitian for a structured, gradual weight loss plan.'
        }

def get_ideal_weight_range(height_cm):
    if not height_cm or height_cm <= 0:
        return (0.0, 0.0)
    height_m = height_cm / 100.0
    min_weight = 18.5 * (height_m * height_m)
    max_weight = 24.9 * (height_m * height_m)
    return (round(min_weight, 1), round(max_weight, 1))
