"""Compile each independent C answer and compare every public sample locally."""
import json
import pathlib
import subprocess
import sys
import shlex
import shutil
import tempfile
import hashlib

ROOT = pathlib.Path(__file__).resolve().parent


def normalize(data):
    return data.replace(b"\r\n", b"\n").rstrip(b"\n")


def check_maze(output, sample_input, samples):
    """Require every simple path, validate numbering, then compare public path matrices."""
    values = list(map(int, sample_input.split()))
    n, m = values[:2]
    maze = values[2:]
    paths = set()
    visited = [0] * (n * m)

    def dfs(r, c):
        if not (0 <= r < n and 0 <= c < m) or not maze[r * m + c] or visited[r * m + c]:
            return
        visited[r * m + c] = 1
        if (r, c) == (n - 1, m - 1):
            paths.add(tuple(visited))
        else:
            for dr, dc in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                dfs(r + dr, c + dc)
        visited[r * m + c] = 0

    dfs(0, 0)
    lines = output.decode("utf-8").splitlines()
    if len(lines) != len(paths) * (n + 1):
        return False
    actual = set()
    for i in range(len(paths)):
        block = lines[i * (n + 1):(i + 1) * (n + 1)]
        if block[0] != str(i + 1):
            return False
        if any(len(row.split()) != m for row in block[1:]):
            return False
        actual.add(tuple(map(int, " ".join(block[1:]).split())))
    public = {tuple(map(int, s["expected"].split())) for s in samples if s["input"] == sample_input}
    return actual == paths and public <= actual


def main():
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    if "--snapshot" in sys.argv:
        index["tasks"] = [json.loads(p.read_text(encoding="utf-8")) for p in ROOT.rglob("task.json")]
    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    results = []
    for task in index["tasks"]:
        directory = ROOT / task["directory"]
        sources = list((directory / "answer").rglob("*.c"))
        result = {"directory": task["directory"], "passed": False, "samples": []}
        result["answer_sha256"] = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory / "answer").rglob("*") if p.is_file()}
        results.append(result)
        if (directory / "skip.json").exists():
            result["skipped"] = json.loads((directory / "skip.json").read_text(encoding="utf-8"))["reason"]
            task["status"] = "skipped_missing_specification"
            (directory / "task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            continue
        if not sources:
            result["error"] = "missing answer"
            continue
        executable = build / f'{task["homework_id"]}-{task["position"]}.exe'
        try:
            compile_result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-finput-charset=UTF-8", "-fexec-charset=UTF-8", *map(str, sources), "-lm", "-o", str(executable)], capture_output=True, timeout=30)
            if compile_result.returncode:
                result["error"] = compile_result.stderr.decode("utf-8", errors="replace").replace(str(ROOT), ".")
                continue
            samples = json.loads((directory / "samples.json").read_text(encoding="utf-8"))
            source = "platform_public"
            if not samples and (directory / "local-tests.json").exists():
                samples = json.loads((directory / "local-tests.json").read_text(encoding="utf-8"))
                source = "statement_derived"
            result["test_source"] = source
            config = json.loads((directory / "run.json").read_text(encoding="utf-8")) if (directory / "run.json").exists() else {}
            for sample in samples:
                if sample["input"] is None or sample["expected"] is None:
                    result["samples"].append({"name": sample["name"], "passed": False, "error": "sample not fully exposed"})
                    continue
                with tempfile.TemporaryDirectory(prefix="run-", dir=build) as temporary:
                    work = pathlib.Path(temporary)
                    for resource in (directory / "resources").rglob("*"):
                        if resource.is_file():
                            target = work / resource.relative_to(directory / "resources")
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(resource, target)
                            shutil.copyfile(resource, work / resource.name)
                    command = [str(executable)]
                    stdin = sample["input"]
                    if config.get("command_line"):
                        first, _, stdin = stdin.partition("\n")
                        command += shlex.split(first)[1:]
                    if config.get("matrix_file"):
                        shutil.copyfile(work / stdin.strip(), work / "matrix.in")
                        stdin = ""
                    run = subprocess.run(command, input=stdin.encode("utf-8"), capture_output=True, timeout=5, cwd=work)
                    actual = run.stdout
                    if config.get("output_file"):
                        output = work / config["output_file"]
                        actual = output.read_bytes() if output.exists() else b""
                    passed = run.returncode == 0 and (check_maze(actual, sample["input"], samples) if config.get("all_paths") else normalize(actual) == normalize(sample["expected"].encode("utf-8")))
                row = {"name": sample["name"], "passed": passed, "exit_code": run.returncode}
                if not passed:
                    row.update(actual=actual.decode("utf-8", errors="replace"), expected=sample["expected"], stderr=run.stderr.decode("utf-8", errors="replace"))
                result["samples"].append(row)
            result["passed"] = bool(samples) and all(s["passed"] for s in result["samples"])
        except (OSError, subprocess.TimeoutExpired) as error:
            result["error"] = str(error).replace(str(ROOT), ".")
        task["status"] = ("public_samples_passed" if result.get("test_source") == "platform_public" else "statement_examples_passed") if result["passed"] else "needs_review"
        (directory / "task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if "--update-index" in sys.argv:
        (ROOT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "verification.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed = sum(r["passed"] for r in results)
    skipped = sum("skipped" in r for r in results)
    print(f"{passed}/{len(results)-skipped} attempted tasks passed; {skipped} skipped")
    for result in results:
        if not result["passed"] and "skipped" not in result:
            print(json.dumps(result, ensure_ascii=False))
    return 0 if passed + skipped == len(results) and not index["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
