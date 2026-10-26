"""Tests for opt-in scoreboard spoiler delay buffering."""

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / "custom_components" / "sports_ticker" / "spoiler_delay.py"
SPEC = importlib.util.spec_from_file_location("spoiler_delay", MODULE)
spoiler_delay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(spoiler_delay)
DelayedScoreboardBuffer = spoiler_delay.DelayedScoreboardBuffer

START = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


class SpoilerDelayBufferTests(unittest.TestCase):
    def test_never_releases_early(self):
        buffer = DelayedScoreboardBuffer(60)
        buffer.enqueue({"events": [{"score": "7"}]}, START)
        self.assertEqual(buffer.next_due, START + timedelta(seconds=60))
        self.assertIsNone(buffer.take_ready(START + timedelta(seconds=59)))
        self.assertEqual(
            buffer.take_ready(START + timedelta(seconds=60))["events"][0]["score"],
            "7",
        )
        self.assertIsNone(buffer.next_due)

    def test_later_score_waits_while_earlier_score_releases(self):
        buffer = DelayedScoreboardBuffer(30)
        buffer.enqueue({"events": [{"score": "3"}]}, START)
        buffer.enqueue({"events": [{"score": "10"}]}, START + timedelta(seconds=15))
        self.assertEqual(
            buffer.take_ready(START + timedelta(seconds=30))["events"][0]["score"],
            "3",
        )
        self.assertIsNone(buffer.take_ready(START + timedelta(seconds=44)))
        self.assertEqual(
            buffer.take_ready(START + timedelta(seconds=45))["events"][0]["score"],
            "10",
        )

    def test_copies_nested_live_data(self):
        buffer = DelayedScoreboardBuffer(90)
        live = {"events": [{"competitions": [{"competitors": [{"score": "0"}]}]}]}
        buffer.enqueue(live, START)
        live["events"][0]["competitions"][0]["competitors"][0]["score"] = "14"
        held = buffer.take_ready(START + timedelta(seconds=90))
        self.assertEqual(
            held["events"][0]["competitions"][0]["competitors"][0]["score"], "0"
        )

    def test_late_scheduler_coalesces_only_due_updates(self):
        buffer = DelayedScoreboardBuffer(60)
        for i in range(4):
            buffer.enqueue({"events": [{"score": i}]}, START + timedelta(seconds=i * 15))
        self.assertEqual(
            buffer.take_ready(START + timedelta(seconds=90))["events"][0]["score"], 2
        )
        self.assertEqual(buffer.next_due, START + timedelta(seconds=105))
        self.assertEqual(
            buffer.take_ready(START + timedelta(seconds=105))["events"][0]["score"], 3
        )

    def test_invalid_off_value_never_enables_buffer(self):
        with self.assertRaises(ValueError):
            DelayedScoreboardBuffer(0)

    def test_stale_payload_is_not_replaced_by_unreleased_live_payload(self):
        buffer = DelayedScoreboardBuffer(120)
        buffer.enqueue({"events": [{"score": "1"}], "_sports_ticker_meta": {"stale": True}}, START)
        buffer.enqueue({"events": [{"score": "2"}], "_sports_ticker_meta": {"stale": False}}, START + timedelta(seconds=30))
        first = buffer.take_ready(START + timedelta(seconds=120))
        self.assertEqual(first["events"][0]["score"], "1")
        self.assertTrue(first["_sports_ticker_meta"]["stale"])
        self.assertIsNone(buffer.take_ready(START + timedelta(seconds=149)))


if __name__ == "__main__":
    unittest.main()
