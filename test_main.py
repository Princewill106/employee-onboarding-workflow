import json
import unittest
from datetime import date

import main


class OnboardingTests(unittest.TestCase):
    def test_business_days(self):
        self.assertEqual(main.add_business_days(date(2026, 10, 12), -3), date(2026, 10, 7))

    def test_overdue(self):
        tpl = json.load(open("templates.json"))
        hire = json.load(open("sample_hires.json"))[0]
        late = main.overdue(main.plan(hire, tpl), date(2026, 10, 9))
        self.assertEqual({t["task"] for t in late}, {"Courier laptop and headset", "Create email and Slack accounts", "Prepare 30-60-90 day plan"})


if __name__ == "__main__":
    unittest.main()
