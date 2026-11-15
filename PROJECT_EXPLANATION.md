# MediQueue — Project Explanation

## 1. Purpose

MediQueue is a menu-driven Python console program that demonstrates how a clinic can organize patient queues. It registers patients, creates tokens, applies priority rules, estimates waiting time, and summarizes the day's served patients.

## 2. Data structures

- `DOCTORS`: a list of dictionaries containing doctor details and average consultation time.
- `patients`: a list of dictionaries. Each dictionary stores one patient's token, details, doctor, priority, status, and timestamps.
- `priority_streak`: a dictionary that stores the senior-priority counter separately for each doctor.

These are in-memory data structures. No database is used.

## 3. Queue algorithm

Priority values are Emergency = 1, Senior Citizen = 2, and Normal = 3. The lowest number represents the highest priority.

For each doctor:
1. Select the earliest waiting emergency patient if one exists.
2. If no emergency is waiting and two seniors have been selected consecutively since the last normal patient, select a normal patient if available.
3. Otherwise select the earliest senior patient and increase the counter.
4. If no senior patient is waiting, select the earliest normal patient and reset the counter.

Registration time and patient ID provide FIFO order within each priority group. Each doctor has an independent fairness counter. Emergency selections do not modify that counter.

## 4. Fairness mechanism

Without a fairness rule, a continuous stream of senior-priority patients could keep normal patients waiting for a very long time. After two senior selections, the program serves one waiting normal patient. This limits starvation while retaining emergency priority.

This is a sample scheduling policy for an academic project; it is not a clinical triage recommendation.

## 5. Waiting-time calculation

The `estimate_wait()` method makes a temporary simulation of the queue. It applies the same emergency and fairness rules until the requested token is selected. It then calculates:

`Estimated wait = (patients scheduled ahead + patients already called) × doctor's average consultation time`

The estimate is approximate because real consultation times differ.

## 6. Patient status operations

A patient can move through these states:

- `Waiting`: registered and waiting.
- `Called`: selected as the next patient.
- `Served`: consultation has been completed.
- `Skipped`: temporarily removed from the active queue.

The Recall option changes a skipped patient back to Waiting.

## 7. Daily summary

For each doctor, the program counts patients whose status is Served and calculates the average time between registration and being called. This is registration-to-call waiting time, not the total consultation duration.

## 8. CSV file

CSV export is optional. It writes the current in-memory patient records to `patients.csv`. The CSV is not a database and is not automatically imported on the next run.

## 9. Important functions

| Function | Purpose |
|---|---|
| `register_patient()` | Validates details, assigns priority, and creates a token |
| `waiting_patients()` | Gets a doctor's waiting patients in FIFO order |
| `_choose_next()` | Applies emergency and fairness rules |
| `call_next()` | Marks the selected patient as Called |
| `mark_served()` | Marks a called patient as Served |
| `skip_patient()` / `recall_patient()` | Handles skipped patients |
| `estimate_wait()` | Simulates queue order and estimates waiting time |
| `daily_summary()` | Calculates per-doctor daily statistics |
| `export_csv()` | Saves records to a CSV file |

## 10. Limitations

The project is an academic prototype. It has no authentication, encryption, clinical validation, or multi-user synchronization. Use fictional patient information during demonstrations.
