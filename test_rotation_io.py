"""Reproduce platform filename input without manufacturing a matrix.in alias."""
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
TASK = next(t for t in json.loads((ROOT / "index.json").read_text(encoding="utf-8"))["tasks"] if (t["homework_id"], t["position"]) == (4139776, 6))
DIRECTORY = ROOT / TASK["directory"]


class RotationIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = ROOT / ".build"
        build.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="rotation-", dir=build)
        cls.root = pathlib.Path(cls.temporary.name)
        cls.executable = cls.root / "rotation.exe"
        result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", str(DIRECTORY / TASK["answer_files"][0]), "-o", str(cls.executable)], capture_output=True, timeout=30)
        if result.returncode:
            cls.temporary.cleanup()
            raise AssertionError(result.stderr.decode("utf-8", errors="replace"))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def run_matrix(self, files, stdin="", arguments=(), expected=None, success=True):
        with tempfile.TemporaryDirectory(prefix="case-", dir=self.root) as temporary:
            work = pathlib.Path(temporary)
            for name, content in files.items():
                path = work / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content.encode("utf-8"))
            run = subprocess.run([str(self.executable), *arguments], input=stdin.encode("utf-8"), capture_output=True, cwd=work, timeout=5)
            self.assertEqual(run.stdout, b"", "The platform prints matrix.out; the answer must not print it twice")
            if success:
                self.assertEqual(run.returncode, 0, run.stderr)
                actual = (work / "matrix.out").read_bytes().replace(b"\r\n", b"\n").rstrip(b"\n")
                self.assertEqual(actual, expected.encode("utf-8"))
            else:
                self.assertNotEqual(run.returncode, 0)
                self.assertFalse((work / "matrix.out").exists())

    def test_public_samples_with_repository_files_only(self):
        samples = json.loads((DIRECTORY / "samples.json").read_text(encoding="utf-8"))
        for sample in samples:
            with self.subTest(sample=sample["name"]):
                name = sample["input"].strip()
                content = (DIRECTORY / "resources/src/step6" / name).read_text(encoding="utf-8")
                self.run_matrix({"src/step6/" + name: content}, stdin=name + "\n", expected=sample["expected"])

    def test_explicit_repository_path(self):
        self.run_matrix({"src/step6/matrix1.in": "2 3\n1 5 3\n3 2 4\n"}, stdin="src/step6/matrix1.in\n", expected="3 4\n5 2\n1 3")

    def test_filename_in_working_directory(self):
        self.run_matrix({"custom.in": "2 2\n1 2\n3 4\n"}, stdin="custom.in\n", expected="2 4\n1 3")

    def test_statement_default_file(self):
        self.run_matrix({"matrix.in": "1 1\n42\n"}, expected="42")

    def test_preinstalled_default_with_filename_input(self):
        self.run_matrix({"matrix.in": "1 2\n7 8\n"}, stdin="matrix1.in\n", expected="8\n7")

    def test_command_line_filename(self):
        self.run_matrix({"custom.in": "3 1\n-1\n0\n9\n"}, arguments=("custom.in",), expected="-1 0 9")

    def test_missing_input(self):
        self.run_matrix({}, stdin="missing.in\n", success=False)

    def test_invalid_dimensions_and_truncated_matrix(self):
        for content in ("0 2\n", "-1 2\n", "2 2\n1 2 3\n"):
            with self.subTest(content=content):
                self.run_matrix({"matrix.in": content}, success=False)


if __name__ == "__main__":
    unittest.main()
