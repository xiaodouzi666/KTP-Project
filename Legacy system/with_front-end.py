import os
import json
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import scrolledtext, messagebox


class KnowledgeBase:
    def __init__(self, directory_path):
        # Initialize the knowledge base with the specified directory path
        self.directory_path = directory_path
        self.data = self.load_all_data()

    def load_all_data(self):
        # Load all JSON files from the specified directory
        all_data = {}
        for file_name in os.listdir(self.directory_path):
            if file_name.endswith(".json"):
                category = file_name.replace(".json", "")
                file_path = os.path.join(self.directory_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        all_data[category] = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error: Failed to decode {file_name}")
        return all_data

    def auto_detect_category(self, user_input):
        # Generate a combined text from all conditions and descriptions
        combined_text = ""
        for category, records in self.data.items():
            for record in records:
                if isinstance(record, dict):
                    conditions = record.get("conditions", {})
                    combined_text += " ".join(
                        conditions.get("symptom", []) +
                        conditions.get("description", [])
                    )
        return combined_text

    @staticmethod
    def similarity(text1, text2):
        # Calculate similarity between two texts using SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def query(self, user_input):
        # Query the knowledge base based on user input
        results = []
        for category, records in self.data.items():
            for record in records:
                combined_conditions = " ".join(record.get("conditions", {}).get("symptom", []) +
                                               record.get("conditions", {}).get("context", []))
                if any(word.lower() in combined_conditions.lower() for word in user_input.split()):
                    results.append(record)
        return results if results else "No relevant records found."


class InferenceEngine:
    def __init__(self, knowledge_base):
        # Initialize the inference engine with the knowledge base
        self.kb = knowledge_base

    def infer(self, user_input):
        # Infer results based on user input
        matches = self.kb.query(user_input)
        if isinstance(matches, str):  # No matching records
            return matches
        if matches:
            return self.generate_dynamic_questions(matches)
        return "No relevant advice found for your input."

    @staticmethod
    def generate_dynamic_questions(matches):
        # Generate dynamic questions based on matching records
        response = "Based on your input, we have the following questions for you:\n"
        for idx, match in enumerate(matches, start=1):
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
        # Initialize the Tkinter application with the knowledge base
        super().__init__()
        self.kb = kb
        self.title("Knowledge Expert System")
        self.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        # Create and arrange widgets for the application
        tk.Label(self, text="Describe your problem or symptom:", font=("Arial", 12)).pack(pady=10)
        self.input_text = tk.Entry(self, width=60, font=("Arial", 12))
        self.input_text.pack(pady=5)
        tk.Button(self, text="Submit", command=self.handle_submit, font=("Arial", 12)).pack(pady=10)
        self.output_area = scrolledtext.ScrolledText(self, width=70, height=15, font=("Arial", 10))
        self.output_area.pack(pady=10)
        self.disclaimer_label = tk.Label(
            self, text=self.DISCLAIMER_TEXT, font=("Arial", 9), wraplength=550, justify="left"
        )
        self.disclaimer_label.pack(pady=5)

    def handle_submit(self):
        # Handle the submit button click event
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
    # Main function to initialize and run the application
    knowledge_base_directory = "./legacy system"  # Adjust path to the legacy system folder
    if not os.path.exists(knowledge_base_directory):
        print(f"Error: Directory '{knowledge_base_directory}' does not exist.")
        return
    kb = KnowledgeBase(knowledge_base_directory)
    app = Application(kb)
    app.mainloop()


if __name__ == "__main__":
    main()
