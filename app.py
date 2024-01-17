from flask import Flask, request, jsonify
import json
from difflib import get_close_matches

app = Flask(__name__)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(user_question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base['question']:
        if q['question'] == user_question:
            return q['answer']
    return None

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('user_input', '').lower()

    knowledge_base = load_knowledge_base('knowledge_base.json')

    if user_input == 'quit':
        return jsonify({"bot_response": "Exiting chat bot"})

    best_match: str | None = find_best_match(user_input, [q['question'] for q in knowledge_base['question']])

    if best_match:
        answer: str = get_answer_for_question(best_match, knowledge_base)
        return jsonify({"bot_response": answer})
    else:
        new_answer: str = data.get('new_answer', '').lower()
        if new_answer != "skip":
            knowledge_base['question'].append({'question': user_input, "answer": new_answer})
            save_knowledge_base('knowledge_base.json', knowledge_base)
            return jsonify({"bot_response": f"Thank you! I learned a new response for '{user_input}'"})
        else:
            return jsonify({"bot_response": "I don't know the answer. Can you teach me?"})

if __name__ == '__main__':
    app.run(debug=True)
