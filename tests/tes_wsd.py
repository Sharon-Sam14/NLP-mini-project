import unittest
from src.wsd.lesk import simplified_lesk

class TestWSD(unittest.TestCase):
    def test_room_hotel_sense(self):
        sentence = "I want to book a hotel bedroom for two nights."
        sense = simplified_lesk("room", sentence)
        self.assertEqual(sense, "hotel")

    def test_charge_fee_sense(self):
        sentence = "What is the total fee and price for the taxi?"
        sense = simplified_lesk("charge", sentence)
        self.assertEqual(sense, "fee")

if __name__ == "__main__":
    unittest.main()