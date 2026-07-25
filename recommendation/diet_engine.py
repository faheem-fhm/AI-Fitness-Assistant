"""
South Indian Regional Diet Recommendation Engine with Strict Preference Filtering
"""
import os
import csv
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEALS_PATH = os.path.join(BASE_DIR, 'dataset', 'south_indian_meals.csv')

class DietEngine:
    def __init__(self):
        self.meals = []
        self._load_meals()

    def _load_meals(self):
        self.meals = []
        if os.path.exists(MEALS_PATH):
            with open(MEALS_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
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
                    self.meals.append(row)

    def generate_plan(self, target_calories=2000.0, diet_pref='any', goal='Gain Muscle'):
        if not self.meals:
            self._load_meals()

        pref_lower = str(diet_pref).lower()

        if 'non' in pref_lower or 'non_vegetarian' in pref_lower:
            # Strictly non-vegetarian items
            filtered = [m for m in self.meals if 'non' in m.get('diet', '').lower() or any(k in m.get('title', '').lower() for k in ['egg', 'chicken', 'fish', 'mutton', 'prawn'])]
        elif 'veg' in pref_lower or 'vegetarian' in pref_lower:
            # Strictly vegetarian items
            filtered = [m for m in self.meals if 'non' not in m.get('diet', '').lower() and not any(k in m.get('title', '').lower() for k in ['egg', 'chicken', 'fish', 'mutton', 'prawn'])]
        else:
            filtered = self.meals

        if not filtered:
            filtered = self.meals

        def get_slot(key, pool):
            items = [m for m in pool if key in m.get('meal_time', '').lower()]
            return items if items else pool

        bf = random.choice(get_slot('breakfast', filtered))
        lu = random.choice(get_slot('lunch', filtered))
        di = random.choice(get_slot('dinner', filtered))
        sn = random.choice(get_slot('snack', filtered) or get_slot('tiffin', filtered) or filtered)

        tot_cal = bf['calories_num'] + lu['calories_num'] + di['calories_num'] + sn['calories_num']
        tot_pro = bf['protein_num'] + lu['protein_num'] + di['protein_num'] + sn['protein_num']
        tot_carbs = bf['carbs_num'] + lu['carbs_num'] + di['carbs_num'] + sn['carbs_num']
        tot_fat = bf['fat_num'] + lu['fat_num'] + di['fat_num'] + sn['fat_num']

        return {
            'breakfast': bf,
            'lunch': lu,
            'dinner': di,
            'snack': sn,
            'total_calories': round(tot_cal, 1),
            'total_protein': round(tot_pro, 1),
            'total_carbs': round(tot_carbs, 1),
            'total_fat': round(tot_fat, 1),
            'water_intake_l': 3.5,
            'goal': goal,
            'diet_pref': diet_pref
        }

diet_engine = DietEngine()
