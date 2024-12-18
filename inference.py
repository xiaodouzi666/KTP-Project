import os
import json
from difflib import SequenceMatcher

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
                        # print(f"Loaded {file_name}: {len(all_data[category])} entries")  # 打印文件名和条目数
                    except json.JSONDecodeError as e:
                        print(f"Error reading {file_name}: {e}")
        # print("All JSON data loaded:", all_data.keys())  # 打印所有加载的类别名称
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
        # print(f"Best-matching category: {best_match} (Score: {highest_score:.2f})")
        return best_match

    @staticmethod
    def similarity(text1, text2):
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def query(self, user_input):
        category = self.auto_detect_category(user_input)
        if not category:
            return "No matching category found."

        # print(f"Searching in category: {category}")
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
        if isinstance(matches, str):
            return matches
        if matches:
            return self.generate_response(matches)
        return "No relevant advice found for your input."

    @staticmethod
    def generate_response(matches):
        """
        Generate a response based on the matched knowledge base entries.
        """
        response = "Here are some recommendations based on your input:\n"
        for idx, match in enumerate(matches, start=1):
            recommendation = match.get("recommendation") or match.get("advice", "No specific recommendation available.")
            response += f"\nRecommendation {idx}:\n"
            response += f"{recommendation}\n"
        return response






def main():
    knowledge_base_directory = "./"  
    kb = KnowledgeBase(knowledge_base_directory)
    engine = InferenceEngine(kb)

    print("Welcome to the Knowledge Expert System!")
    while True:
        user_input = input("\nDescribe your problem or symptom (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = engine.infer(user_input)
        print("\n" + response)


if __name__ == "__main__":
    main()
