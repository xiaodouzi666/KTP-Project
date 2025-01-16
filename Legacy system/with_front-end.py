import os
import json
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import scrolledtext, messagebox


class KnowledgeBase:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.data = self.load_all_data()

    def load_all_data(self):
        all_data = {}
        for file_name in os.listdir(self.directory_path):
            if file_name.endswith(".json"):
                category = file_name.replace(".json", "")
                file_path = os.path.join(self.directory_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        all_data[category] = json.load(file)
                    except json.JSONDecodeError:
                        pass
        return all_data

    def auto_detect_category(self, user_input):
        best_match = None
        highest_score = 0
        for category, records in self.data.items():
            for record in records:
                combined_text = " ".join(record.get("conditions", {}).get("symptom", []) +
                                         record.get("conditions", {}).get("context", []))
                score = self.similarity(user_input, combined_text)
                if score > highest_score:
                    highest_score = score
                    best_match = category
        return best_match

    @staticmethod
    def similarity(text1, text2):
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def query(self, user_input):
        category = self.auto_detect_category(user_input)
        if not category:
            return "No matching category found."

        results = []
        for record in self.data.get(category, []):
            combined_conditions = " ".join(record.get("conditions", {}).get("symptom", []) +
                                           record.get("conditions", {}).get("context", []))
            if any(word.lower() in combined_conditions.lower() for word in user_input.split()):
                results.append(record)

        return results


class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def infer(self, user_input):
        matches = self.kb.query(user_input)
        if isinstance(matches, str):  # No matching category found
            return matches
        if matches:
            return self.generate_dynamic_questions(matches)
        return "No relevant advice found for your input."

    @staticmethod
    def generate_dynamic_questions(matches):
        response = "Based on your input, we have the following questions for you:\n"
        for idx, match in enumerate(matches, start=1):
            # Retrieve the first context question from the match
            question = match.get("conditions", {}).get("context", ["No follow-up question available."])[0]
            response += f"\nQuestion {idx}: {question}"
        response += "\n\nPlease answer these questions to help us better understand your concerns."
        return response



class Application(tk.Tk):
    DISCLAIMER_TEXT = (
        "\n\nDisclaimer:\n"
        "This system is not a substitute for professional medical or therapeutic advice.\n"
        "If you are experiencing a medical or mental health emergency, please seek immediate help\n"
        "from a qualified healthcare professional or appropriate authority."
    )

    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.title("Knowledge Expert System")
        self.geometry("600x500")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Describe your problem or symptom:", font=("Arial", 12)).pack(pady=10)

        self.input_text = tk.Entry(self, width=60, font=("Arial", 12))
        self.input_text.pack(pady=5)

        tk.Button(self, text="Submit", command=self.handle_submit, font=("Arial", 12)).pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(self, width=70, height=15, font=("Arial", 10))
        self.output_area.pack(pady=10)

        # Add disclaimer section at the bottom
        self.disclaimer_label = tk.Label(self, text=self.DISCLAIMER_TEXT, font=("Arial", 9), wraplength=550, justify="left")
        self.disclaimer_label.pack(pady=5)

    def handle_submit(self):
        user_input = self.input_text.get().strip()
        if not user_input:
            messagebox.showwarning("Input Error", "Please enter a description of your problem.")
            return

        engine = InferenceEngine(self.kb)
        response = engine.infer(user_input)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, response)
        self.output_area.insert(tk.END, self.DISCLAIMER_TEXT)  # Append disclaimer to output area


def main():
    knowledge_base_directory = "./" 
    kb = KnowledgeBase(knowledge_base_directory)
    app = Application(kb)
    app.mainloop()


if __name__ == "__main__":
    main()
