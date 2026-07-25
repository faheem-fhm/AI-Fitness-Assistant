"""
AI Workout Routine Generator Engine for 7-Day and 30-Day Plans
"""
from models.exercise import load_all_exercises

class WorkoutEngine:
    def __init__(self):
        pass

    def generate_routine(self, plan_type='7-Day Workout', goal='Gain Muscle', location='Gym Workout', split='Push Pull Legs', level='Beginner'):
        all_ex = load_all_exercises()

        # Filter by location if Home Workout (Bodyweight only)
        if 'home' in str(location).lower() or 'bodyweight' in str(location).lower():
            all_ex = [e for e in all_ex if 'body' in e['equipment'].lower() or 'band' in e['equipment'].lower() or 'mat' in e['equipment'].lower()] or all_ex

        def get_by_bp(bp_keys):
            return [e for e in all_ex if any(k in e['bodyPart'].lower() or k in e['target'].lower() for k in bp_keys)]

        chest = get_by_bp(['chest']) or all_ex[:4]
        back = get_by_bp(['back', 'lat', 'rhomboid']) or all_ex[4:8]
        legs = get_by_bp(['leg', 'quad', 'hamstring', 'glute']) or all_ex[8:12]
        shoulders = get_by_bp(['shoulder', 'delt']) or all_ex[12:16]
        arms = get_by_bp(['upper arm', 'bicep', 'tricep']) or all_ex[16:20]
        core = get_by_bp(['waist', 'cardio']) or all_ex[20:24]

        days = []

        if '30' in str(plan_type):
            # 30-Day Workout Plan Breakdown (Weeks 1 to 4)
            weeks = [
                ('Week 1: Foundations & Adaption', [
                    {'day': 'Day 1: Chest & Shoulders', 'routine': chest[:3] + shoulders[:2]},
                    {'day': 'Day 2: Back & Biceps', 'routine': back[:3] + arms[:2]},
                    {'day': 'Day 3: Legs & Core', 'routine': legs[:3] + core[:2]},
                    {'day': 'Day 4: Active Recovery', 'routine': []},
                    {'day': 'Day 5: Full Body Conditioning', 'routine': [chest[0], back[0], legs[0], core[0]]},
                    {'day': 'Day 6: Mobility & Cardio', 'routine': core[:3]},
                    {'day': 'Day 7: Rest Day', 'routine': []}
                ]),
                ('Week 2: Hypertrophy Focus', [
                    {'day': 'Day 8: Push Focus (Chest/Delts/Triceps)', 'routine': chest[1:4] + shoulders[1:3]},
                    {'day': 'Day 9: Pull Focus (Lats/Rear Delts/Biceps)', 'routine': back[1:4] + arms[1:3]},
                    {'day': 'Day 10: Quads & Glutes Blast', 'routine': legs[1:4]},
                    {'day': 'Day 11: Rest & Recovery', 'routine': []},
                    {'day': 'Day 12: Upper Body Sculpt', 'routine': chest[:2] + back[:2] + shoulders[:1]},
                    {'day': 'Day 13: Lower Body & Abs', 'routine': legs[:2] + core[:2]},
                    {'day': 'Day 14: Rest Day', 'routine': []}
                ]),
                ('Week 3: Peak Volume & Intensity', [
                    {'day': 'Day 15: Heavy Chest & Triceps', 'routine': chest[:3] + arms[2:4]},
                    {'day': 'Day 16: Heavy Back & Biceps', 'routine': back[:3] + arms[:2]},
                    {'day': 'Day 17: Heavy Legs & Calves', 'routine': legs[:4]},
                    {'day': 'Day 18: Rest & Active Recovery', 'routine': []},
                    {'day': 'Day 19: Shoulder & Arm Supersets', 'routine': shoulders[:3] + arms[:3]},
                    {'day': 'Day 20: Core Burnout & HIIT', 'routine': core[:4]},
                    {'day': 'Day 21: Rest Day', 'routine': []}
                ]),
                ('Week 4: Deload & Progressive Overload', [
                    {'day': 'Day 22: Full Body Power A', 'routine': [chest[0], back[0], legs[0]]},
                    {'day': 'Day 23: Rest', 'routine': []},
                    {'day': 'Day 24: Full Body Power B', 'routine': [shoulders[0], arms[0], core[0]]},
                    {'day': 'Day 25: Active Walk & Stretch', 'routine': []},
                    {'day': 'Day 26: Upper Body Mastery', 'routine': chest[:2] + back[:2]},
                    {'day': 'Day 27: Lower Body Mastery', 'routine': legs[:3]},
                    {'day': 'Day 28-30: Final Recovery & Metric Assessment', 'routine': []}
                ])
            ]
            
            # Flatten 30-Day schedule for rendering
            for week_title, week_days in weeks:
                days.append({'day': f'--- {week_title} ---', 'routine': []})
                days.extend(week_days)

        else:
            # 7-Day Workout Routine according to split
            split_lower = str(split).lower()

            if 'full body' in split_lower:
                days = [
                    {'day': 'Day 1: Full Body Workout A (Compound Heavy)', 'routine': [chest[0], back[0], legs[0], shoulders[0]]},
                    {'day': 'Day 2: Active Recovery & Mobility', 'routine': []},
                    {'day': 'Day 3: Full Body Workout B (Hypertrophy)', 'routine': [chest[1], back[1], legs[1], arms[0]]},
                    {'day': 'Day 4: Rest Day', 'routine': []},
                    {'day': 'Day 5: Full Body Workout C (Core & Endurance)', 'routine': [legs[2], back[2], shoulders[1], core[0]]},
                    {'day': 'Day 6: Cardio & Abs Core', 'routine': core[:3]},
                    {'day': 'Day 7: Full Rest', 'routine': []}
                ]
            elif 'bro' in split_lower:
                days = [
                    {'day': 'Day 1: Chest Destruction', 'routine': chest[:4]},
                    {'day': 'Day 2: Back & Lats Width', 'routine': back[:4]},
                    {'day': 'Day 3: Shoulder & Traps Sculpt', 'routine': shoulders[:4]},
                    {'day': 'Day 4: Leg Day Strength', 'routine': legs[:4]},
                    {'day': 'Day 5: Arms (Biceps & Triceps)', 'routine': arms[:4]},
                    {'day': 'Day 6: Core & Cardio Burn', 'routine': core[:3]},
                    {'day': 'Day 7: Rest & Recovery', 'routine': []}
                ]
            else: # Push Pull Legs
                days = [
                    {'day': 'Day 1: Push (Chest, Shoulders, Triceps)', 'routine': chest[:2] + shoulders[:1] + arms[:1]},
                    {'day': 'Day 2: Pull (Back, Biceps, Rear Delts)', 'routine': back[:3] + arms[1:2]},
                    {'day': 'Day 3: Legs & Lower Abs', 'routine': legs[:3] + core[:1]},
                    {'day': 'Day 4: Active Recovery & Flexibility', 'routine': core[:2]},
                    {'day': 'Day 5: Push Focus Hypertrophy', 'routine': chest[2:4] + shoulders[1:2]},
                    {'day': 'Day 6: Pull & Legs Combo', 'routine': back[3:5] + legs[3:5]},
                    {'day': 'Day 7: Full Rest & Hydration', 'routine': []}
                ]

        return {
            'plan_name': f'{level} {split} ({location}) - {goal}',
            'duration': plan_type,
            'warmup': '5-10 mins dynamic stretching (Arm circles, Leg swings, High knees)',
            'cooldown': '5-10 mins static stretching & foam rolling',
            'safety_tips': 'Prioritize proper form over weight. Stay hydrated and track progression.',
            'days': days
        }

workout_engine = WorkoutEngine()
