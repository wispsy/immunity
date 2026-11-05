"""Tests for plugin specification parser."""

import tempfile
import unittest
from pathlib import Path

from immunity.parser import parse_plugin_line, parse_plugins_file, parse_plugins_text


class TestParser(unittest.TestCase):
    def test_empty_and_comments(self) -> None:
        self.assertIsNone(parse_plugin_line(""))
        self.assertIsNone(parse_plugin_line("   "))
        self.assertIsNone(parse_plugin_line("# This is a comment"))
        self.assertIsNone(parse_plugin_line("   # Indented comment"))

    def test_shorthand_github_repo(self) -> None:
        spec = parse_plugin_line("zsh-users/zsh-autosuggestions")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.name, "zsh-autosuggestions")
        self.assertEqual(spec.target, "zsh-users/zsh-autosuggestions")
        self.assertEqual(spec.url, "https://github.com/zsh-users/zsh-autosuggestions.git")
        self.assertIsNone(spec.ref)
        self.assertIsNone(spec.subpath)
        self.assertEqual(spec.kind, "plugin")
        self.assertEqual(spec.cache_key, "github.com/zsh-users/zsh-autosuggestions")

    def test_repo_with_ref_and_directives(self) -> None:
        line = "romkatv/powerlevel10k@v1.20.0 path:sub kind:theme defer:2 pick:p10k.zsh"
        spec = parse_plugin_line(line)
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.name, "powerlevel10k")
        self.assertEqual(spec.ref, "v1.20.0")
        self.assertEqual(spec.subpath, "sub")
        self.assertEqual(spec.kind, "theme")
        self.assertEqual(spec.defer, 2)
        self.assertEqual(spec.pick, "p10k.zsh")

    def test_full_git_urls(self) -> None:
        https_spec = parse_plugin_line("https://gitlab.com/example/my-plugin.git")
        self.assertIsNotNone(https_spec)
        assert https_spec is not None
        self.assertEqual(https_spec.name, "my-plugin")
        self.assertEqual(https_spec.url, "https://gitlab.com/example/my-plugin.git")
        self.assertEqual(https_spec.cache_key, "gitlab.com/example/my-plugin")

        ssh_spec = parse_plugin_line("git@github.com:someone/repo.git")
        self.assertIsNotNone(ssh_spec)
        assert ssh_spec is not None
        self.assertEqual(ssh_spec.name, "repo")
        self.assertEqual(ssh_spec.cache_key, "github.com/someone/repo")

    def test_parse_plugins_file(self) -> None:
        content = """
        # Zsh plugins list
        zsh-users/zsh-autosuggestions
        zsh-users/zsh-syntax-highlighting

        # Completion only
        zsh-users/zsh-completions kind:fpath
        """
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write(content)
            tf.flush()
            temp_path = Path(tf.name)

        try:
            specs = parse_plugins_file(temp_path)
            self.assertEqual(len(specs), 3)
            self.assertEqual(specs[0].name, "zsh-autosuggestions")
            self.assertEqual(specs[1].name, "zsh-syntax-highlighting")
            self.assertEqual(specs[2].name, "zsh-completions")
            self.assertEqual(specs[2].kind, "fpath")
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
