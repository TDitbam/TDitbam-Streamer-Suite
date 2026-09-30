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

            self.assertTrue(os.path.isfile(path))
            self.assertEqual(
                {"Settings", "Targets", "PopularGames", "Paths", "Presets"},
                set(config.sections()),
            )
            self.assertEqual("5", config["Settings"]["interval"])
            self.assertTrue(config["Settings"].getboolean("exclude_core_0"))
            self.assertFalse(config["Settings"].getboolean("disable_smt"))
            self.assertEqual(0, len(config["Targets"]))
            self.assertEqual(0, len(config["Paths"]))
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

    def test_first_run_defaults_remain_user_editable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                config = config_loader.load_config()
                config["Settings"]["interval"] = "12"
                config["Settings"]["exclude_core_0"] = "false"
                config["Targets"]["my-game.exe"] = "NORMAL"
                config_loader.save_config(config)
                reloaded = config_loader.load_config()

            self.assertEqual("12", reloaded["Settings"]["interval"])
            self.assertFalse(
                reloaded["Settings"].getboolean("exclude_core_0")
            )
            self.assertEqual("NORMAL", reloaded["Targets"]["my-game.exe"])

    def test_reset_config_replaces_custom_values_with_ready_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "optimizer_config.ini")
            with patch.object(config_loader, "get_opt_config_path", return_value=path):
                config = config_loader.load_config()
                config["Settings"]["interval"] = "30"
                config["Targets"]["my-game.exe"] = "NORMAL"
                config["Paths"]["c:\\games"] = "E-CORE"
                config.remove_option("PopularGames", "cs2.exe")
                config_loader.save_config(config)

                reset = config_loader.reset_config()
                reloaded = config_loader.load_config()

            self.assertEqual("5", reset["Settings"]["interval"])
            self.assertEqual(0, len(reset["Targets"]))
            self.assertEqual(0, len(reset["Paths"]))
            self.assertEqual("P-CORE", reset["PopularGames"]["cs2.exe"])
            self.assertEqual(
                dict(reset.items("Settings")),
                dict(reloaded.items("Settings")),
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
