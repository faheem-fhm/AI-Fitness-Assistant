"""
Exercise Recommendation Engine over 870+ ExerciseDB Records
"""
from models.exercise import load_all_exercises

class ExerciseEngine:
    def __init__(self):
        pass

    def recommend(self, goal='Gain Muscle', difficulty=None, body_part=None, equipment=None, user_weight_kg=70.0, limit=6):
        all_ex = load_all_exercises(user_weight_kg)
        filtered = []

        g_lower = str(goal).lower()
        bp_lower = str(body_part).lower() if body_part else None
        eq_lower = str(equipment).lower() if equipment else None
        diff_lower = str(difficulty).lower() if difficulty else None

        for ex in all_ex:
            # Body part filter
            if bp_lower and bp_lower != 'all':
                if bp_lower not in ex['bodyPart'].lower() and bp_lower not in ex['target'].lower():
                    continue

            # Equipment filter
            if eq_lower and eq_lower != 'all':
                if eq_lower not in ex['equipment'].lower():
                    continue

            # Difficulty filter
            if diff_lower and diff_lower != 'all':
                if diff_lower != ex['difficulty'].lower():
                    continue

            filtered.append(ex)

        if not filtered:
            filtered = all_ex

        recommendations = []
        for ex in filtered[:limit]:
            if 'muscle' in g_lower or 'hypertrophy' in g_lower:
                sets, reps, rest = '4', '8-12 reps', '60-90 sec'
            elif 'fat' in g_lower or 'cardio' in g_lower:
                sets, reps, rest = '3-4', '12-15 reps', '30-45 sec'
            elif 'strength' in g_lower:
                sets, reps, rest = '5', '5 reps', '2-3 min'
            else:
                sets, reps, rest = '3', '12-15 reps / hold 30s', '45 sec'

            ex_copy = dict(ex)
            ex_copy['recommended_sets'] = sets
            ex_copy['recommended_reps'] = reps
            ex_copy['recommended_rest'] = rest
            recommendations.append(ex_copy)

        return recommendations

exercise_engine = ExerciseEngine()
