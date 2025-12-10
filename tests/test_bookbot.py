import importlib
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure required environment variables are present before importing bookbot
ENV_VARS = {
    "API_TOKEN": "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "POCKETBOOK_EMAIL": "pb@example.com",
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_PORT": "587",
    "EMAIL_ADDRESS": "bot@example.com",
    "EMAIL_PASSWORD": "password",
    "BOT_MODE": "polling",
}

env_patch = mock.patch.dict(os.environ, ENV_VARS)
env_patch.start()
import bookbot  # noqa: E402  pylint: disable=wrong-import-position

# Reload to guarantee environment patch applies if bookbot was imported elsewhere
bookbot = importlib.reload(bookbot)


def tearDownModule():  # noqa: D401
    """Stop environment patching after module tests complete."""

    env_patch.stop()


class ValidateBotModeTests(unittest.TestCase):
    def test_accepts_supported_modes(self):
        self.assertEqual(bookbot.validate_bot_mode("polling"), "polling")
        self.assertEqual(bookbot.validate_bot_mode("WEBHOOK"), "webhook")

    def test_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            bookbot.validate_bot_mode("invalid")


class ExtensionCheckTests(unittest.TestCase):
    def test_allows_supported_extensions_case_insensitive(self):
        self.assertTrue(bookbot._is_allowed_extension("Title.PDF"))
        self.assertTrue(bookbot._is_allowed_extension("book.epub"))

    def test_rejects_unsupported_extension(self):
        self.assertFalse(bookbot._is_allowed_extension("notes.docx"))


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        bookbot.user_send_history.clear()

    @mock.patch("bookbot.time.time", return_value=1_000)
    def test_limits_after_maximum_within_window(self, _):
        user_id = 123
        for _ in range(bookbot.MAX_FILES_PER_HOUR):
            self.assertFalse(bookbot._rate_limited(user_id))
        self.assertTrue(bookbot._rate_limited(user_id))

    def test_expired_entries_are_removed(self):
        user_id = 456
        timestamps = [0] * bookbot.MAX_FILES_PER_HOUR + [3_601]
        with mock.patch("bookbot.time.time", side_effect=timestamps):
            for _ in range(bookbot.MAX_FILES_PER_HOUR):
                self.assertFalse(bookbot._rate_limited(user_id))
            self.assertFalse(bookbot._rate_limited(user_id))
        self.assertEqual(len(bookbot.user_send_history[user_id]), 1)


class DownloadWithRetryTests(IsolatedAsyncioTestCase):
    async def test_download_retries_then_succeeds(self):
        mock_bot = mock.AsyncMock()
        file_info = types.SimpleNamespace(file_path="remote/path")
        mock_bot.get_file.return_value = file_info
        mock_bot.download_file.side_effect = [Exception("fail"), None]

        with mock.patch.object(bookbot, "bot", mock_bot), mock.patch(
            "bookbot.asyncio.sleep", new=mock.AsyncMock()
        ) as sleep_mock:
            await bookbot._download_file_with_retry("file_id", "dest")

        self.assertEqual(mock_bot.download_file.call_count, 2)
        sleep_mock.assert_awaited()


class SendToPocketbookTests(IsolatedAsyncioTestCase):
    async def test_send_email_retries_on_failure(self):
        send_mock = mock.Mock(side_effect=[Exception("smtp"), None])

        async def immediate_to_thread(func, *args, **kwargs):
            return func(*args, **kwargs)

        with mock.patch.object(bookbot, "_send_email", send_mock), mock.patch(
            "bookbot.asyncio.sleep", new=mock.AsyncMock()
        ) as sleep_mock, mock.patch(
            "bookbot.asyncio.to_thread", side_effect=immediate_to_thread
        ) as thread_mock:
            await bookbot.send_to_pocketbook("/tmp/file", "file.epub")

        self.assertEqual(send_mock.call_count, 2)
        thread_mock.assert_called()
        sleep_mock.assert_awaited()


if __name__ == "__main__":
    unittest.main()
