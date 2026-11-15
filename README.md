# MediQueue — Priority-Based Patient Queue Management System

**Project Code:** CP-021  
**Language:** Python 3  
**Application:** Menu-driven console application

MediQueue is a small clinic queue-management prototype. It registers patients, assigns tokens, maintains a separate queue for each doctor, applies priority and fairness rules, estimates waiting time, and displays a daily summary.

## Assignment requirements

- Python console application with a menu
- No GUI
- No website
- No database
- Patient records are kept in memory while the program runs
- Optional CSV export is included as a stretch feature

## Features

1. Register a patient and generate a date-based token.
2. Select one of three sample doctors.
3. Automatically assign priority:
   - Emergency: highest priority
   - Senior citizen: age 60 or above
   - Normal: all other patients
4. Call the next patient using the priority/fairness algorithm.
5. Skip a patient and recall a skipped patient.
6. Estimate waiting time for a waiting token.
7. View today's served-patient count and average registration-to-call wait per doctor.
8. Export the current session's records to `patients.csv`.

## Queue algorithm

Each doctor has an independent queue and fairness counter.

1. If an emergency patient is waiting, call the earliest registered emergency patient.
2. Otherwise, if two senior-priority patients have been selected since the last normal patient and a normal patient is waiting, call the earliest registered normal patient.
3. Otherwise, call the earliest registered senior patient and increase the senior counter.
4. If no senior patient is waiting, call the earliest registered normal patient and reset the counter.
5. Emergency calls do not change the senior/normal fairness counter.

Patients within the same priority category are served in registration order (FIFO).

The fairness rule is an academic demonstration policy, not a medical triage standard. Emergency status should only be assigned or confirmed by qualified clinical staff in a real healthcare setting.

## Waiting-time calculation

The program simulates the same scheduling algorithm until it reaches the requested token. It counts the patients scheduled ahead, adds any patient already marked `Called`, and multiplies that total by the selected doctor's sample average consultation time.

`Estimated wait = (patients ahead + currently called patients) × average consultation minutes`

The result is approximate because actual consultation durations can vary.

## Run the project

Install Python 3, then open a terminal in the project folder and run:

```bash
python main.py
```

On some Windows installations, use:

```bash
py main.py
```

No third-party packages or database setup are required.

## CSV export

Choose **8. Save Records to CSV** in the menu. The program creates `patients.csv` in the same folder as `main.py`.

The application does not automatically load old CSV records on startup. Patient data remains in memory only for the current run; export the records before exiting if you need to keep them.

## Project structure

```text
MediQueue/
├── main.py
├── README.md
├── .gitignore
├── docs/
│   └── PROJECT_EXPLANATION.md
└── tests/
    └── test_mediqueue.py
```

## Testing

Run the included unit tests:

```bash
python -m unittest discover -s tests -v
```

## Limitations

- This is an educational prototype, not a clinically validated or production-ready hospital system.
- Data is stored in memory during a run unless exported to CSV.
- The sample doctor consultation durations are fixed values.
- No login, access control, encryption, or multi-computer synchronization is provided.
- Use fictional patient details for demonstrations.
