import configparser
import os
import tempfile
import unittest
from unittest.mock import patch

from optimizer.optimizer_core import config_loader
from optimizer.optimizer_core.game_presets import POPULAR_GAME_PRESETS


class PopularGamePresetTests(unittest.TestCase):
    def test_new_config_contains_curated_game_presets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                config = config_loader.load_config()

            self.assertGreaterEqual(len(config["PopularGames"]), 75)
            self.assertEqual("P-CORE", config["PopularGames"]["cs2.exe"])
            self.assertEqual(
                "P-CORE",
                config["PopularGames"]["FortniteClient-Win64-Shipping.exe"],
            )
            self.assertNotIn("javaw.exe", config["PopularGames"])
            self.assertFalse(
                any(name.endswith(".tmp") for name in os.listdir(directory))
            )

    def test_migration_preserves_existing_user_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            existing = configparser.ConfigParser(delimiters=("=",))
            existing["Settings"] = {"interval": "10"}
            existing["Targets"] = {
                "cs2.exe": "E-CORE",
                "my-custom-game.exe": "NORMAL",
            }
            existing["Paths"] = {}
            with open(path, "w", encoding="utf-8") as config_file:
                existing.write(config_file)

            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                migrated = config_loader.load_config()

            active_targets = dict(config_loader.get_targets(migrated))
            self.assertEqual("E-CORE", active_targets["cs2.exe"])
            self.assertEqual(
                "NORMAL", active_targets["my-custom-game.exe"]
            )
            self.assertEqual("10", migrated["Settings"]["interval"])
            self.assertEqual(2, len(migrated["Targets"]))
            self.assertEqual(
                len(POPULAR_GAME_PRESETS), len(migrated["PopularGames"])
            )

    def test_removed_preset_is_not_readded_on_every_load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                config = config_loader.load_config()
                config.remove_option("PopularGames", "cs2.exe")
                config_loader.save_config(config)
                reloaded = config_loader.load_config()

            self.assertNotIn("cs2.exe", reloaded["PopularGames"])

    def test_focused_update_preserves_concurrent_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                config_loader.update_config(
                    lambda config: config["Targets"].__setitem__(
                        "stream-game.exe", "P-CORE"
                    )
                )
                updated = config_loader.update_config(
                    lambda config: config["Settings"].__setitem__(
                        "last_cleanup", "12345"
                    )
                )

            self.assertEqual("P-CORE", updated["Targets"]["stream-game.exe"])
            self.assertEqual("12345", updated["Settings"]["last_cleanup"])


if __name__ == "__main__":
    unittest.main()
