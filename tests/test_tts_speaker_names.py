import unittest
from unittest.mock import patch

from core.tts_engine import ChatTTSEngine


class TTSSpeakerNameTests(unittest.TestCase):
    def setUp(self):
        with patch.object(ChatTTSEngine, "_ensure_directories"), patch.object(
            ChatTTSEngine, "_load_profanity_list"
        ):
            self.engine = ChatTTSEngine()

    def test_skips_name_only_for_consecutive_messages_from_same_user(self):
        self.assertEqual(
            "Alice พูดว่า ข้อความแรก",
            self.engine._process_message(
                {"author": "Alice", "message": "ข้อความแรก"}
            ),
        )
        self.assertEqual(
            "ข้อความถัดไป",
            self.engine._process_message(
                {"author": "Alice", "message": "ข้อความถัดไป"}
            ),
        )
        self.assertEqual(
            "Bob พูดว่า สวัสดี",
            self.engine._process_message({"author": "Bob", "message": "สวัสดี"}),
        )
        self.assertEqual(
            "Alice พูดว่า กลับมาแล้ว",
            self.engine._process_message(
                {"author": "Alice", "message": "กลับมาแล้ว"}
            ),
        )

    def test_marks_only_actual_speaker_transitions_for_delay(self):
        self.assertEqual(
            ("Alice พูดว่า หนึ่ง", False),
            self.engine._prepare_message({"author": "Alice", "message": "หนึ่ง"}),
        )
        self.assertEqual(
            ("สอง", False),
            self.engine._prepare_message({"author": "Alice", "message": "สอง"}),
        )
        self.assertEqual(
            ("Bob พูดว่า สาม", True),
            self.engine._prepare_message({"author": "Bob", "message": "สาม"}),
        )
        self.assertEqual(
            ("Alice พูดว่า สี่", True),
            self.engine._prepare_message({"author": "Alice", "message": "สี่"}),
        )

    def test_speaker_change_delay_is_bounded_and_interruptible(self):
        self.assertEqual(0.0, self.engine._coerce_speaker_change_delay(-1))
        self.assertEqual(10.0, self.engine._coerce_speaker_change_delay(20))
        self.assertEqual(0.75, self.engine._coerce_speaker_change_delay("invalid"))

        stop_event = unittest.mock.Mock()
        stop_event.wait.return_value = False
        self.engine.speaker_change_delay = 1.25

        self.assertFalse(self.engine._wait_for_speaker_change(False, stop_event))
        stop_event.wait.assert_not_called()
        self.assertFalse(self.engine._wait_for_speaker_change(True, stop_event))
        stop_event.wait.assert_called_once_with(1.25)

    def test_filtered_message_does_not_change_last_spoken_user(self):
        self.assertEqual(
            "Alice พูดว่า เริ่ม",
            self.engine._process_message({"author": "Alice", "message": "เริ่ม"}),
        )

        self.assertIsNone(
            self.engine._process_message({"author": "Bob", "message": "x" * 201})
        )

        self.assertEqual(
            "ต่อ",
            self.engine._process_message({"author": "Alice", "message": "ต่อ"}),
        )

    def test_removes_colon_wrapped_emoji_codes_before_tts(self):
        self.assertEqual(
            "Alice พูดว่า สวัสดี",
            self.engine._process_message(
                {"author": "Alice", "message": ":หัวใจ: สวัสดี :smile:"}
            ),
        )
        self.assertEqual(
            "ไป กัน",
            self.engine._process_message(
                {"author": "Alice", "message": "ไป :dance: กัน"}
            ),
        )

    def test_emoji_only_message_is_skipped_without_changing_speaker(self):
        self.assertEqual(
            "Alice พูดว่า เริ่ม",
            self.engine._process_message({"author": "Alice", "message": "เริ่ม"}),
        )
        self.assertIsNone(
            self.engine._prepare_message(
                {"author": "Bob", "message": ":หัวใจ: :smile:"}
            )
        )
        self.assertEqual(
            "ต่อ",
            self.engine._process_message({"author": "Alice", "message": "ต่อ"}),
        )

    def test_shortcode_filter_preserves_times_urls_and_plain_text(self):
        message = "เจอกัน 12:30:45 ที่ https://example.com/path"
        self.assertEqual(
            f"Alice พูดว่า {message}",
            self.engine._process_message({"author": "Alice", "message": message}),
        )
        self.assertIsNone(self.engine._process_message(":emoji:"))
        self.assertEqual("ประกาศแล้ว", self.engine._process_message("ประกาศแล้ว :bell:"))

    def test_stopping_resets_last_spoken_user(self):
        self.engine._process_message({"author": "Alice", "message": "ก่อนหยุด"})

        with patch.object(self.engine, "_clear_queues"), patch.object(
            self.engine, "_cleanup_temp_files"
        ):
            self.engine._stop_locked()

        self.assertEqual(
            "Alice พูดว่า เริ่มใหม่",
            self.engine._process_message(
                {"author": "Alice", "message": "เริ่มใหม่"}
            ),
        )


if __name__ == "__main__":
    unittest.main()
