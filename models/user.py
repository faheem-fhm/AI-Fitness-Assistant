"""
User Data Model & Progress Analytics Engine
"""
from utils.bmi import calculate_bmi, get_bmi_category, get_ideal_weight_range
from utils.bmr import calculate_bmr, calculate_tdee
from utils.calorie import calculate_daily_targets

class UserModel:
    def __init__(self, user_dict):
        if hasattr(user_dict, 'keys'):
            user_dict = dict(user_dict)
        elif not isinstance(user_dict, dict):
            user_dict = {}

        self.id = user_dict.get('id')
        self.username = user_dict.get('username', 'Fitness Fan')
        self.email = user_dict.get('email', '')
        self.age = int(user_dict.get('age') or 25)
        self.height = float(user_dict.get('height') or 175.0)
        self.weight = float(user_dict.get('weight') or 70.0)
        self.gender = str(user_dict.get('gender') or 'male')
        self.goal = str(user_dict.get('goal') or 'Gain Muscle')
        self.is_admin = bool(user_dict.get('is_admin', 0))

    def get_bmi(self):
        return calculate_bmi(self.weight, self.height)

    def get_bmi_info(self):
        return get_bmi_category(self.get_bmi())

    def get_ideal_weight(self):
        return get_ideal_weight_range(self.height)

    def get_daily_targets(self):
        return calculate_daily_targets(self.weight, self.height, self.age, self.gender, self.goal)
