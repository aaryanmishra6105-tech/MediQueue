"""
MediQueue - Priority-Based Patient Queue Management System
Foundation project | Python 3 | Menu-driven console application

Run: python main.py
Optional CSV export: choose option 8 from the menu.
No GUI, website, external packages, or database are required.
"""

import csv
from datetime import date, datetime
from pathlib import Path

DOCTORS = [
    {"id": 1, "name": "Dr. Sharma", "specialization": "General Physician", "avg_minutes": 10},
    {"id": 2, "name": "Dr. Reddy", "specialization": "Pediatrician", "avg_minutes": 12},
    {"id": 3, "name": "Dr. Khan", "specialization": "Cardiologist", "avg_minutes": 15},
]

PRIORITY_NAMES = {1: "Emergency", 2: "Senior Citizen", 3: "Normal"}
CSV_FILE = Path(__file__).with_name("patients.csv")


def now_text():
    """Return the current local date and time in a consistent format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class MediQueue:
    """Stores patients in memory and applies the queue scheduling rules."""

    def __init__(self):
        self.patients = []
        self.next_patient_id = 1
        # Fairness counter is independent for each doctor.
        self.priority_streak = {doctor["id"]: 0 for doctor in DOCTORS}

    @staticmethod
    def get_doctor(doctor_id):
        for doctor in DOCTORS:
            if doctor["id"] == doctor_id:
                return doctor
        return None

    def register_patient(self, name, age, phone, doctor_id, emergency=False):
        """Register a patient, assign priority, and issue a daily token."""
        if not name.strip():
            raise ValueError("Patient name cannot be empty.")
        if not isinstance(age, int) or not 0 <= age <= 120:
            raise ValueError("Age must be between 0 and 120.")
        if self.get_doctor(doctor_id) is None:
            raise ValueError("Please select a valid doctor.")

        if emergency:
            priority = 1
        elif age >= 60:
            priority = 2
        else:
            priority = 3

        today = date.today().strftime("%Y%m%d")
        todays_count = sum(p["token"].startswith(today + "-") for p in self.patients)
        token = f"{today}-{todays_count + 1:03d}"

        patient = {
            "id": self.next_patient_id,
            "token": token,
            "name": name.strip(),
            "age": age,
            "phone": phone.strip(),
            "doctor_id": doctor_id,
            "doctor_name": self.get_doctor(doctor_id)["name"],
            "priority": priority,
            "status": "Waiting",
            "registered_at": now_text(),
            "called_at": "",
            "served_at": "",
            "skipped_at": "",
        }
        self.next_patient_id += 1
        self.patients.append(patient)
        return patient

    def waiting_patients(self, doctor_id):
        """Return waiting patients in registration order."""
        return sorted(
            [p for p in self.patients
             if p["doctor_id"] == doctor_id and p["status"] == "Waiting"],
            key=lambda p: (p["registered_at"], p["id"])
        )

    def _choose_next(self, queue, doctor_id, update_fairness):
        """Choose a patient using emergency priority and senior/normal fairness."""
        if not queue:
            return None

        emergencies = [p for p in queue if p["priority"] == 1]
        if emergencies:
            # Emergency patients do not change the senior/normal fairness counter.
            return emergencies[0]

        seniors = [p for p in queue if p["priority"] == 2]
        normals = [p for p in queue if p["priority"] == 3]
        streak = self.priority_streak[doctor_id]

        if normals and streak >= 2:
            chosen = normals[0]
            new_streak = 0
        elif seniors:
            chosen = seniors[0]
            new_streak = streak + 1
        elif normals:
            chosen = normals[0]
            new_streak = 0
        else:
            return None

        if update_fairness:
            self.priority_streak[doctor_id] = new_streak
        return chosen

    def call_next(self, doctor_id):
        """Call the next patient for one doctor."""
        queue = self.waiting_patients(doctor_id)
        chosen = self._choose_next(queue, doctor_id, update_fairness=True)
        if chosen is None:
            return None
        chosen["status"] = "Called"
        chosen["called_at"] = now_text()
        return chosen

    def mark_served(self, token):
        patient = self.find_patient(token)
        if not patient or patient["status"] != "Called":
            return False
        patient["status"] = "Served"
        patient["served_at"] = now_text()
        return True

    def skip_patient(self, token):
        patient = self.find_patient(token)
        if not patient or patient["status"] not in ("Waiting", "Called"):
            return False
        patient["status"] = "Skipped"
        patient["skipped_at"] = now_text()
        return True

    def recall_patient(self, token):
        patient = self.find_patient(token)
        if not patient or patient["status"] != "Skipped":
            return False
        patient["status"] = "Waiting"
        patient["called_at"] = ""
        patient["skipped_at"] = ""
        return True

    def find_patient(self, token):
        token = token.strip()
        return next((p for p in self.patients if p["token"] == token), None)

    def estimate_wait(self, token):
        """Simulate the queue policy and estimate minutes before a waiting token."""
        target = self.find_patient(token)
        if not target or target["status"] != "Waiting":
            return None

        doctor_id = target["doctor_id"]
        remaining = self.waiting_patients(doctor_id)
        streak = self.priority_streak[doctor_id]
        patients_ahead = 0

        while remaining:
            emergencies = [p for p in remaining if p["priority"] == 1]
            seniors = [p for p in remaining if p["priority"] == 2]
            normals = [p for p in remaining if p["priority"] == 3]

            if emergencies:
                chosen = emergencies[0]
            elif normals and streak >= 2:
                chosen = normals[0]
                streak = 0
            elif seniors:
                chosen = seniors[0]
                streak += 1
            elif normals:
                chosen = normals[0]
                streak = 0
            else:
                break

            if chosen["token"] == token:
                active_called = sum(
                    1 for p in self.patients
                    if p["doctor_id"] == doctor_id and p["status"] == "Called"
                )
                doctor = self.get_doctor(doctor_id)
                return (patients_ahead + active_called) * doctor["avg_minutes"]

            patients_ahead += 1
            remaining.remove(chosen)
        return None

    def daily_summary(self):
        """Return today's served count and average registration-to-call wait per doctor."""
        today = date.today().isoformat()
        summary = []
        for doctor in DOCTORS:
            served = [
                p for p in self.patients
                if p["doctor_id"] == doctor["id"]
                and p["status"] == "Served"
                and p["registered_at"].startswith(today)
                and p["called_at"]
            ]
            waits = []
            for patient in served:
                start = datetime.strptime(patient["registered_at"], "%Y-%m-%d %H:%M:%S")
                called = datetime.strptime(patient["called_at"], "%Y-%m-%d %H:%M:%S")
                waits.append((called - start).total_seconds() / 60)
            average = sum(waits) / len(waits) if waits else None
            summary.append({
                "doctor": doctor["name"],
                "served": len(served),
                "average_wait": average,
            })
        return summary

    def export_csv(self, filename=CSV_FILE):
        """Save all current session records to a CSV file."""
        fields = [
            "token", "name", "age", "phone", "doctor_name", "priority",
            "status", "registered_at", "called_at", "served_at", "skipped_at"
        ]
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for patient in self.patients:
                row = {field: patient[field] for field in fields}
                row["priority"] = PRIORITY_NAMES[patient["priority"]]
                writer.writerow(row)
        return filename


def print_header():
    print("\n" + "=" * 54)
    print("                    MEDIQUEUE")
    print("          Hospital Queue Management System")
    print("=" * 54)


def choose_doctor():
    print("\nAvailable doctors:")
    for doctor in DOCTORS:
        print(
            f"{doctor['id']}. {doctor['name']} - {doctor['specialization']} "
            f"(Average consultation: {doctor['avg_minutes']} min)"
        )
    while True:
        try:
            choice = int(input("Select doctor number: ").strip())
            if MediQueue.get_doctor(choice):
                return choice
            print("Invalid doctor number. Try again.")
        except ValueError:
            print("Enter a number.")


def display_patients(patients):
    if not patients:
        print("\nNo patient records found.")
        return
    print("\n" + "-" * 100)
    print(f"{'TOKEN':<17} {'PATIENT':<20} {'AGE':<5} {'PRIORITY':<17} {'STATUS':<10}")
    print("-" * 100)
    for p in patients:
        print(
            f"{p['token']:<17} {p['name'][:19]:<20} {p['age']:<5} "
            f"{PRIORITY_NAMES[p['priority']]:<17} {p['status']:<10}"
        )
    print("-" * 100)


def register_menu(system):
    print("\n--- Patient Registration ---")
    name = input("Patient name: ").strip()
    try:
        age = int(input("Age: ").strip())
    except ValueError:
        print("Invalid age. Registration cancelled.")
        return
    phone = input("Phone number (optional): ").strip()
    doctor_id = choose_doctor()
    emergency_answer = input("Emergency case? (y/n): ").strip().lower()
    emergency = emergency_answer == "y"
    try:
        patient = system.register_patient(name, age, phone, doctor_id, emergency)
        print("\nPatient registered successfully.")
        print(f"Token    : {patient['token']}")
        print(f"Doctor   : {patient['doctor_name']}")
        print(f"Priority : {PRIORITY_NAMES[patient['priority']]}")
    except ValueError as error:
        print(f"Registration failed: {error}")


def view_queue_menu(system):
    doctor_id = choose_doctor()
    doctor = system.get_doctor(doctor_id)
    rows = [
        p for p in system.patients
        if p["doctor_id"] == doctor_id and p["status"] in ("Waiting", "Called", "Skipped")
    ]
    print(f"\n--- Queue for {doctor['name']} ---")
    display_patients(rows)


def call_next_menu(system):
    doctor_id = choose_doctor()
    patient = system.call_next(doctor_id)
    if patient:
        print(f"\nNow calling: {patient['token']} - {patient['name']}")
        print(f"Priority: {PRIORITY_NAMES[patient['priority']]}")
    else:
        print("\nThere are no waiting patients for this doctor.")


def token_action_menu(system, action):
    token = input("Enter patient token: ").strip()
    if action == "skip":
        success = system.skip_patient(token)
        message = "Patient skipped. Use Recall to return them to the queue."
    else:
        success = system.recall_patient(token)
        message = "Patient returned to the waiting queue."
    print(message if success else "Action not possible. Check the token and patient status.")


def estimate_menu(system):
    token = input("Enter patient token: ").strip()
    minutes = system.estimate_wait(token)
    if minutes is None:
        print("Token not found or patient is not currently waiting.")
    else:
        print(f"Estimated waiting time for {token}: about {minutes} minutes.")
        print("This is an estimate, not a guaranteed appointment time.")


def summary_menu(system):
    print("\n--- Today's Daily Summary ---")
    print(f"{'DOCTOR':<22} {'PATIENTS SERVED':<18} {'AVG WAIT (MIN)':<16}")
    print("-" * 60)
    for row in system.daily_summary():
        average = "—" if row["average_wait"] is None else f"{row['average_wait']:.1f}"
        print(f"{row['doctor']:<22} {row['served']:<18} {average:<16}")
    print("-" * 60)


def main():
    system = MediQueue()
    actions = {
        "1": lambda: register_menu(system),
        "2": lambda: view_queue_menu(system),
        "3": lambda: call_next_menu(system),
        "4": lambda: token_action_menu(system, "skip"),
        "5": lambda: token_action_menu(system, "recall"),
        "6": lambda: estimate_menu(system),
        "7": lambda: summary_menu(system),
    }

    while True:
        print_header()
        print("1. Register Patient")
        print("2. View Doctor Queue")
        print("3. Call Next Patient")
        print("4. Skip Patient")
        print("5. Recall Patient")
        print("6. Estimate Waiting Time")
        print("7. View Daily Summary")
        print("8. Save Records to CSV")
        print("9. Exit")
        choice = input("\nEnter your choice (1-9): ").strip()

        if choice in actions:
            actions[choice]()
        elif choice == "8":
            path = system.export_csv()
            print(f"\nRecords saved successfully to: {path}")
        elif choice == "9":
            print("\nThank you for using MediQueue. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select a number from 1 to 9.")

        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
