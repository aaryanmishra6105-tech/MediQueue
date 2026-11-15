import unittest
from main import MediQueue, PRIORITY_NAMES


class MediQueueTests(unittest.TestCase):
    def setUp(self):
        self.system = MediQueue()
        self.doctor_id = 1

    def add(self, name, age=30, emergency=False):
        return self.system.register_patient(name, age, "", self.doctor_id, emergency)

    def test_priority_assignment(self):
        self.assertEqual(self.add("Normal")["priority"], 3)
        self.assertEqual(self.add("Senior", 60)["priority"], 2)
        self.assertEqual(self.add("Emergency", 25, True)["priority"], 1)

    def test_emergency_is_called_first(self):
        normal = self.add("Normal")
        emergency = self.add("Emergency", 25, True)
        self.assertEqual(self.system.call_next(self.doctor_id)["token"], emergency["token"])

    def test_normal_patient_after_two_seniors(self):
        senior1 = self.add("Senior One", 65)
        senior2 = self.add("Senior Two", 70)
        normal = self.add("Normal")
        self.assertEqual(self.system.call_next(self.doctor_id)["token"], senior1["token"])
        self.assertEqual(self.system.call_next(self.doctor_id)["token"], senior2["token"])
        self.assertEqual(self.system.call_next(self.doctor_id)["token"], normal["token"])

    def test_fifo_within_same_priority(self):
        first = self.add("First", 62)
        self.add("Second", 68)
        self.assertEqual(self.system.call_next(self.doctor_id)["token"], first["token"])

    def test_skip_and_recall(self):
        patient = self.add("Patient")
        self.assertTrue(self.system.skip_patient(patient["token"]))
        self.assertTrue(self.system.recall_patient(patient["token"]))
        self.assertEqual(self.system.find_patient(patient["token"])["status"], "Waiting")

    def test_wait_estimate(self):
        first = self.add("First")
        second = self.add("Second")
        self.assertEqual(self.system.estimate_wait(first["token"]), 0)
        self.assertEqual(self.system.estimate_wait(second["token"]), 10)

    def test_doctor_queues_are_independent(self):
        patient = self.add("Doctor One")
        other = self.system.register_patient("Doctor Two", 30, "", 2)
        called = self.system.call_next(2)
        self.assertEqual(called["token"], other["token"])
        self.assertEqual(self.system.find_patient(patient["token"])["status"], "Waiting")


if __name__ == "__main__":
    unittest.main()
