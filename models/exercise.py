"""
Exercise Model with Automatic Difficulty Classifier and MET Calorie Burn Calculator
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXERCISES_JSON_PATH = os.path.join(BASE_DIR, 'dataset', 'exercises.json')

class ExerciseModel:
    def __init__(self, data):
        self.id = str(data.get('id', ''))
        self.name = str(data.get('name', '')).title()
        self.bodyPart = str(data.get('bodyPart', 'waist')).lower()
        self.equipment = str(data.get('equipment', 'body weight')).lower()
        self.target = str(data.get('target', 'full body')).lower()
        self.secondaryMuscles = data.get('secondaryMuscles', '')
        self.category = str(data.get('category', 'strength')).lower()
        self.instructions = str(data.get('instructions', ''))
        self.gifUrl = data.get('gifUrl') or data.get('image') or 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500'
        self.image = self.gifUrl

        # Automatic Difficulty Classifier
        self.difficulty = self.classify_difficulty()

        # Dynamic MET (Metabolic Equivalent of Task) assignment
        self.met = self.assign_met()

    def classify_difficulty(self):
        eq = self.equipment.lower()
        mech = str(self.target).lower()

        if any(k in eq for k in ['barbell', 'olympic', 'smith machine']) or 'deadlift' in self.name.lower() or 'squat' in self.name.lower():
            return 'Advanced'
        elif any(k in eq for k in ['dumbbell', 'cable', 'kettlebell', 'ez barbell', 'machine']):
            return 'Intermediate'
        else: # body weight, body only, band, stretch
            return 'Beginner'

    def assign_met(self):
        cat = self.category.lower()
        eq = self.equipment.lower()

        if 'cardio' in cat or 'running' in self.name.lower():
            return 8.0
        elif 'plyometrics' in cat or 'burpee' in self.name.lower():
            return 8.5
        elif 'barbell' in eq or 'powerlifting' in cat:
            return 6.0
        elif 'dumbbell' in eq or 'cable' in eq:
            return 5.0
        elif 'stretching' in cat or 'yoga' in cat:
            return 2.5
        else: # General bodyweight conditioning
            return 4.0

    def calculate_calories_burned(self, weight_kg=70.0, duration_minutes=15.0):
        """
        Formula: Calories Burned = MET x Weight (kg) x Duration (hours)
        """
        if not weight_kg or weight_kg <= 0:
            weight_kg = 70.0
        hours = float(duration_minutes) / 60.0
        cals = self.met * float(weight_kg) * hours
        return round(cals, 1)

    def to_dict(self, user_weight_kg=70.0):
        return {
            'id': self.id,
            'name': self.name,
            'bodyPart': self.bodyPart,
            'equipment': self.equipment,
            'target': self.target,
            'secondaryMuscles': self.secondaryMuscles,
            'category': self.category,
            'instructions': self.instructions,
            'gifUrl': self.gifUrl,
            'image': self.image,
            'difficulty': self.difficulty,
            'met': self.met,
            'caloriesBurned': self.calculate_calories_burned(user_weight_kg, 15.0)
        }

def load_all_exercises(user_weight_kg=70.0):
    exercises = []
    if os.path.exists(EXERCISES_JSON_PATH):
        with open(EXERCISES_JSON_PATH, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            for item in raw:
                ex_obj = ExerciseModel(item)
                exercises.append(ex_obj.to_dict(user_weight_kg))
    return exercises
