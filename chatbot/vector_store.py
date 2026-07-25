"""
Production Vector Store for 870+ ExerciseDB Records & South Indian Meals Dataset
"""
import os
import json
import csv
from chatbot.embeddings import tokenize, get_tf, cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXERCISES_JSON_PATH = os.path.join(BASE_DIR, 'dataset', 'exercises.json')
MEALS_PATH = os.path.join(BASE_DIR, 'dataset', 'south_indian_meals.csv')

class VectorStore:
    def __init__(self):
        self.exercise_docs = []
        self.meal_docs = []
        self.is_indexed = False

    def build_index(self):
        self.exercise_docs = []
        self.meal_docs = []

        if os.path.exists(EXERCISES_JSON_PATH):
            with open(EXERCISES_JSON_PATH, 'r', encoding='utf-8') as f:
                raw_ex = json.load(f)
                for row in raw_ex:
                    text_blob = f"{row.get('name', '')} {row.get('bodyPart', '')} {row.get('target', '')} {row.get('equipment', '')} {row.get('category', '')} {row.get('instructions', '')} {row.get('secondaryMuscles', '')}"
                    tokens = tokenize(text_blob)
                    self.exercise_docs.append({
                        'data': row,
                        'text': text_blob,
                        'tf': get_tf(tokens)
                    })

        if os.path.exists(MEALS_PATH):
            with open(MEALS_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text_blob = f"{row.get('title', '')} {row.get('ingredients', '')} {row.get('diet', '')} {row.get('meal_time', '')} {row.get('dish_type', '')}"
                    tokens = tokenize(text_blob)
                    self.meal_docs.append({
                        'data': row,
                        'text': text_blob,
                        'tf': get_tf(tokens)
                    })

        self.is_indexed = True

    def search_exercises(self, query, top_k=5):
        if not self.is_indexed:
            self.build_index()
        q_tf = get_tf(tokenize(query))
        scored = []
        for doc in self.exercise_docs:
            score = cosine_similarity(q_tf, doc['tf'])
            if score > 0.001:
                scored.append((score, doc['data']))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def search_meals(self, query, top_k=5):
        if not self.is_indexed:
            self.build_index()
        q_tf = get_tf(tokenize(query))
        scored = []
        for doc in self.meal_docs:
            score = cosine_similarity(q_tf, doc['tf'])
            if score > 0.001:
                scored.append((score, doc['data']))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def get_dataset_stats(self):
        if not self.is_indexed:
            self.build_index()

        ex_list = [d['data'] for d in self.exercise_docs]
        meal_list = [d['data'] for d in self.meal_docs]

        body_parts = sorted(list(set(e.get('bodyPart', '').title() for e in ex_list if e.get('bodyPart'))))
        target_muscles = sorted(list(set(e.get('target', '').title() for e in ex_list if e.get('target'))))
        equipments = sorted(list(set(e.get('equipment', '').title() for e in ex_list if e.get('equipment'))))
        categories = sorted(list(set(e.get('category', '').title() for e in ex_list if e.get('category'))))

        return {
            'total_exercises': len(ex_list),
            'total_south_indian_meals': len(meal_list),
            'body_parts': body_parts,
            'target_muscles': target_muscles,
            'equipments': equipments,
            'categories': categories,
            'exercise_fields': ['id', 'name', 'bodyPart', 'equipment', 'target', 'secondaryMuscles', 'category', 'instructions', 'gifUrl'],
            'meal_fields': ['title', 'ingredients', 'state', 'diet', 'meal_time', 'dish_type', 'calories', 'protein', 'fat', 'carbs']
        }

vector_store = VectorStore()
