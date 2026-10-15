"""Compile exact submission files with real platform entry points, then run samples."""
import json
import pathlib
import subprocess
import sys
import shlex
import shutil
import tempfile
import hashlib
import os
import re

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
    selected = None
    if "--task" in sys.argv:
        selected = tuple(map(int, sys.argv[sys.argv.index("--task") + 1].split(":")))
        if len(selected) != 2 or not any((t["homework_id"], t["position"]) == selected for t in index["tasks"]):
            raise ValueError("--task must identify an existing homework_id:position")
    if "--snapshot" in sys.argv:
        index["tasks"] = [json.loads(p.read_text(encoding="utf-8")) for p in ROOT.rglob("task.json")]
    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    results = []
    for task in index["tasks"]:
        if selected and (task["homework_id"], task["position"]) != selected:
            continue
        directory = ROOT / task["directory"]
        submission = json.loads((directory / "submission.json").read_text(encoding="utf-8")) if (directory / "submission.json").exists() else None
        result = {"directory": task["directory"], "passed": False, "samples": []}
        result["answer_sha256"] = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory / "answer").rglob("*") if p.is_file()}
        results.append(result)
        if (directory / "skip.json").exists():
            result["skipped"] = json.loads((directory / "skip.json").read_text(encoding="utf-8"))["reason"]
            task["status"] = "skipped_missing_specification"
            (directory / "task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            continue
        executable = build / f'{task["homework_id"]}-{task["position"]}.exe'
        try:
            if not submission:
                raise ValueError("missing submission contract")
            result["submission_form"] = submission["form"]
            actual_files = {p.relative_to(directory / "answer").as_posix() for p in (directory / "answer").rglob("*") if p.is_file()}
            if actual_files != set(task["editable_paths"]) or actual_files != {f["platform_path"] for f in submission["files"]}:
                raise ValueError("submission files do not match exact platform editable paths")
            for item in submission["files"]:
                if item["answer"] != "answer/" + item["platform_path"]:
                    raise ValueError("invalid answer-to-platform mapping")
            if submission["form"] == "expression":
                for path in actual_files:
                    expression = (directory / "answer" / path).read_text(encoding="utf-8")
                    if ";" in expression or "#" in expression or re.search(r"\bmain\s*\(", expression):
                        raise ValueError("expression contains a statement or program")
            if submission["form"] == "header_functions":
                for path in actual_files:
                    if path.endswith(".h") and re.search(r"\bmain\s*\(", (directory / "answer" / path).read_text(encoding="utf-8")):
                        raise ValueError("function header defines a local main")
            config = json.loads((directory / "run.json").read_text(encoding="utf-8")) if (directory / "run.json").exists() else {}
            with tempfile.TemporaryDirectory(prefix="compile-", dir=build) as temporary:
                tree = pathlib.Path(temporary)
                platform = directory / "harness/platform"
                if platform.exists():
                    shutil.copytree(platform, tree, dirs_exist_ok=True)
                shutil.copytree(directory / "answer", tree, dirs_exist_ok=True)
                paths = {p.relative_to(directory / "answer").as_posix() for p in (directory / "answer").rglob("*.c")}
                if submission["form"] in ("expression", "header_functions"):
                    records = json.loads((directory / "harness/platform-sources.json").read_text(encoding="utf-8"))
                    if not records:
                        raise ValueError("missing real platform entry point")
                    paths.update(record["path"] for record in records)
                    result["entry_point_source"] = "platform_repository"
                    result["platform_entry_sha256"] = {record["path"]: hashlib.sha256((platform / record["path"]).read_bytes()).hexdigest() for record in records}
                else:
                    result["entry_point_source"] = "submission"
                if not paths:
                    raise ValueError("missing compilation entry point")
                sources = [tree / path for path in sorted(paths)]
                flags = []
                if os.name == "nt" and (directory / "harness/random_compat.h").exists():
                    flags = ["-include", str(directory / "harness/random_compat.h")]
                    result["local_adapter"] = "glibc random sequence for Windows only; not submitted"
                compile_result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-finput-charset=UTF-8", "-fexec-charset=UTF-8", *flags, *map(str, sources), "-lm", "-o", str(executable)], capture_output=True, timeout=30)
            if compile_result.returncode:
                result["error"] = compile_result.stderr.decode("utf-8", errors="replace").replace(str(ROOT), ".")
                task["status"] = "needs_review"
                (directory / "task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                continue
            samples = json.loads((directory / "samples.json").read_text(encoding="utf-8"))
            source = "platform_public"
            if not samples and (directory / "local-tests.json").exists():
                samples = json.loads((directory / "local-tests.json").read_text(encoding="utf-8"))
                source = "statement_derived"
            result["test_source"] = source
            samples = [dict(s, source=source) for s in samples]
            if (directory / "contract-tests.json").exists():
                samples += [dict(s, source="local_contract_boundary") for s in json.loads((directory / "contract-tests.json").read_text(encoding="utf-8"))]
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
                    expected_exit = config.get("expected_exit_code", 0)
                    passed = run.returncode == expected_exit and (check_maze(actual, sample["input"], samples) if config.get("all_paths") else normalize(actual) == normalize(sample["expected"].encode("utf-8")))
                row = {"name": sample["name"], "source": sample["source"], "passed": passed, "exit_code": run.returncode, "expected_exit_code": expected_exit}
                if not passed:
                    row.update(actual=actual.decode("utf-8", errors="replace"), expected=sample["expected"], stderr=run.stderr.decode("utf-8", errors="replace"))
                result["samples"].append(row)
            result["passed"] = bool(samples) and all(s["passed"] for s in result["samples"])
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            result["error"] = str(error).replace(str(ROOT), ".")
        task["status"] = ("public_samples_passed" if result.get("test_source") == "platform_public" else "statement_examples_passed") if result["passed"] else "needs_review"
        (directory / "task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if "--update-index" in sys.argv:
        (ROOT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive_results = results
    if selected:
        existing = json.loads((ROOT / "verification.json").read_text(encoding="utf-8"))
        by_directory = {r["directory"]: r for r in existing}
        by_directory.update({r["directory"]: r for r in results})
        archive_results = [by_directory[t["directory"]] for t in index["tasks"]]
    (ROOT / "verification.json").write_text(json.dumps(archive_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed = sum(r["passed"] for r in results)
    skipped = sum("skipped" in r for r in results)
    print(f"{passed}/{len(results)-skipped} attempted tasks passed; {skipped} skipped")
    for result in results:
        if not result["passed"] and "skipped" not in result:
            print(json.dumps(result, ensure_ascii=False))
    return 0 if passed + skipped == len(results) and not index["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
