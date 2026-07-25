"""
Workout Log & Progress Tracking Data Model
"""
class WorkoutLogModel:
    def __init__(self, record):
        if hasattr(record, 'keys'):
            record = dict(record)
        elif not isinstance(record, dict):
            record = {}

        self.id = record.get('id')
        self.user_id = record.get('user_id')
        self.exercise_name = record.get('exercise_name', 'Workout Session')
        self.sets = int(record.get('sets', 3))
        self.reps = int(record.get('reps', 10))
        self.weight_kg = float(record.get('weight_kg', 0.0))
        self.calories_burned = float(record.get('calories_burned', 100.0))
        self.recorded_at = record.get('recorded_at')
