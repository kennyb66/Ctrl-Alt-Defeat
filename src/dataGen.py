# dataGen.py
import json
import base64
import random
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "questions.dat"

def load_questions():
    with open(DATA_PATH, "r") as f:
        encoded = f.read()
    decoded = base64.b64decode(encoded).decode("utf-8")
    data = json.loads(decoded)
    return data["questions"]  # list of all questions

class QuestionManager:
    def __init__(self):
        self.all_questions = load_questions()
        self.asked = set()  # track asked question IDs

    def get_questions_for_boss(self, boss_id):
        return [q for q in self.all_questions if q["bossId"] == boss_id]

    def get_random_question(self, boss_id):
        available = [q for q in self.get_questions_for_boss(boss_id) if q["id"] not in self.asked]
        if not available:
            return None
        q = random.choice(available)
        self.asked.add(q["id"])
        return q
