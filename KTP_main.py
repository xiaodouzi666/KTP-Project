import tkinter as tk
from tkinter import messagebox
import json
import sys
import subprocess  # Import for launching the legacy system

# Initialize the main window
window = tk.Tk()
window.geometry("1200x800")
window.configure(background='#FF69B4')

user_answer_var = tk.StringVar()

# Layout configuration
for i in range(3):
    window.columnconfigure(i, weight=1, minsize=200)
    window.rowconfigure(i, weight=1, minsize=200)

main_frame = tk.Frame(window, height=400, width=300, background="white")
main_frame.grid(row=1, column=1)

# Utility functions


def clear_frame():
    # Clear all widgets from the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()


def update_text_frame(txt):
    # Update the main frame with text content
    label = tk.Label(main_frame, text=txt, bg='white')
    label.pack(pady=20)


def update_title_frame(txt):
    # Update the main frame with a title
    title = tk.Label(main_frame, text=txt, font=(
        "Arial", 16, "bold"), bg='white')
    title.pack(pady=10)


def read_file(filename):
    # Read data from a JSON file
    with open(filename, "r") as file:
        return json.load(file)


def update_file(data, filename):
    # Write updated data to a JSON file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def reset_facts(data, filename):
    # Reset facts in the JSON file
    data["Facts"] = []
    update_file(data, filename)


def on_closing():
    # Handle window closing event
    user_answer_var.set("close")
    window.destroy()


def welcome(data, filename):
    # Display the welcome screen
    clear_frame()
    welcome_msg = tk.Label(
        main_frame, text="Welcome to the Knowledge-Based Therapy System!", bg='white', font=("Arial", 14))
    welcome_msg.pack(pady=20)

    start_btn = tk.Button(main_frame, text="Start",
                          command=lambda: execute_knowledge_base(data, filename))
    start_btn.pack(pady=10)

    # Add legacy system button
    legacy_btn = tk.Button(window, text="Legacy System",
                           command=open_legacy_system, font=("Arial", 10))
    legacy_btn.place(x=10, y=10)  # Position at the top-left corner


def open_legacy_system():
    # Launch the legacy system script
    try:
        subprocess.Popen(
            ["python", "legacy system/with_front-end.py"], shell=True)
    except Exception as e:
        # Display an error message if launching fails
        messagebox.showerror("Error", f"Failed to open legacy system: {e}")


def new_question(question):
    # Display a new question on the main frame
    clear_frame()
    question_label = tk.Label(
        main_frame, text=question, bg='white', font=("Arial", 12))
    question_label.pack(pady=20)

    yes_btn = tk.Button(main_frame, text="Yes",
                        command=lambda: user_answer_var.set("yes"))
    yes_btn.pack(side=tk.LEFT, padx=20, pady=10)

    no_btn = tk.Button(main_frame, text="No",
                       command=lambda: user_answer_var.set("no"))
    no_btn.pack(side=tk.RIGHT, padx=20, pady=10)

    print(f"Question displayed: {question}")  # Log question displayed

# Logic for finding disorders and rules


def find_disorder(current_disorder, knowledge_base):
    # Find a disorder in the knowledge base by its name
    for disorder in knowledge_base:
        if disorder["Disorder"] == current_disorder:
            return disorder
    return None


def evaluate_condition(condition, facts):
    # Evaluate a condition against the collected facts
    if not condition:
        return False

    # Support parsing AND and OR conditions
    conditions = condition.split(" AND ")
    for cond in conditions:
        symptom_name = cond.split("==")[1].strip().strip("'")
        if f"no {symptom_name}" in facts:  # Negative check
            return False
        if symptom_name not in facts:  # Positive check
            return False
    return True


def rule_deduction(facts, rules):
    # Deduce the next step or action based on rules
    for rule in rules:
        condition = rule.get("Condition")
        if evaluate_condition(condition, facts):
            print(f"Condition met: {condition}")
            return rule.get("Action")
        else:
            print(f"Condition not met: {condition}. Current facts: {facts}")

    # Return default advice if no rules are matched
    return "No specific issues detected. Please seek general guidance or consult a professional."


def execute_knowledge_base(data, filename):
    # Execute the knowledge base to provide advice
    knowledge_base = data["Knowledge base"]
    facts = data["Facts"]

    results = {}  # Store advice for each category

    for disorder in knowledge_base:
        current_disorder = disorder["Disorder"]
        disorder_data = find_disorder(current_disorder, knowledge_base)
        if not disorder_data:
            messagebox.showerror("Error", f"Disorder"
                                 " '{current_disorder}' not found in the knowledge base.")
            continue

        # Ask questions and update facts
        for symptom in disorder_data.get("Symptoms", []):
            if symptom["Name"] not in facts:
                new_question(symptom["Questions"][0])
                main_frame.wait_variable(user_answer_var)
                user_response = user_answer_var.get()
                if user_response == "yes":
                    facts.append(symptom["Name"])
                elif user_response == "no":
                    facts.append(f"no {symptom['Name']}")
                elif user_response == "close":
                    sys.exit()
                else:
                    messagebox.showerror("Error", "Invalid response received.")
                update_file(data, filename)

        # Deduce next step or action
        action = rule_deduction(facts, disorder_data.get("Rules", []))
        if action:
            results[current_disorder] = action

    # Display the final results
    clear_frame()
    update_title_frame("Conclusion")
    for category, advice in results.items():
        update_text_frame(f"{category}: {advice}")

    # Add disclaimer to ensure it's visible at the end
    disclaimer_text = (
        "\n\nDisclaimer:\n"
        "This system is not a substitute for professional medical or therapeutic advice.\n"
        "If you are experiencing a medical or mental health emergency, please seek immediate help\n"
        "from a qualified healthcare professional or appropriate authority."
    )
    disclaimer_label = tk.Label(
        main_frame,
        text=disclaimer_text,
        font=("Arial", 9),
        bg='white',
        wraplength=800,  # Ensure the text wraps within the frame width
        justify="left"
    )
    # Pack with padding and anchor to ensure it stays at the bottom
    disclaimer_label.pack(pady=20, anchor="s")


def main():
    # Main function to initialize the program
    filename = "knowledge_base.json"
    data = read_file(filename)
    reset_facts(data, filename)
    welcome(data, filename)


if __name__ == "__main__":
    main()
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()
