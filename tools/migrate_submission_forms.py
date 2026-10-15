"""One-time, reproducible migration from the original standalone-answer commit.

Inputs are read from Git commit 70fc848, so header extraction never uses a test stub.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "70fc848b189fe41153d9d5f58c5bccb9ccdefa32"


def old_file(directory, name):
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{BASE}:{directory}/{name}"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8")


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.replace("\r\n", "\n").encode("utf-8"))


EXPRESSIONS = {
    1: "(((unsigned short)k >> 8) | (((unsigned short)p & 0xffu) << 8))",
    2: "(x = (int)(((unsigned int)x >> ((unsigned int)n & 31u)) | ((unsigned int)x << ((32u - ((unsigned int)n & 31u)) & 31u))))",
    3: "(x = (int)((unsigned int)x ^ (n == 0 ? 0u : n == 32 ? ~0u : ((1u << n) - 1u) << (p - n + 1))))",
    4: "(a > b ? (a > c ? a : c) : (b > c ? b : c))",
    5: "(a % 3 == 0 && a % 10 == 5)",
}

SELECTION = """#include <stdio.h>
void inArray(int arr[], int n) {
    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);
}
void selectSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int smallest = i;
        for (int j = i + 1; j < n; j++) if (arr[j] < arr[smallest]) smallest = j;
        int temp = arr[i]; arr[i] = arr[smallest]; arr[smallest] = temp;
    }
}
void outArray(int arr[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
}
"""

PALINDROME = """#include <stdio.h>
#include <stdlib.h>
/* C_NODE is defined by the platform before including this file. */
void createLinkList(C_NODE **headp, char s[]) {
    *headp = NULL;
    C_NODE **tail = headp;
    while (*s) {
        *tail = malloc(sizeof **tail);
        if (!*tail) exit(EXIT_FAILURE);
        (*tail)->data = *s++;
        (*tail)->next = NULL;
        tail = &(*tail)->next;
    }
}
static C_NODE *reverseHalf(C_NODE *head) {
    C_NODE *previous = NULL;
    while (head) {
        C_NODE *next = head->next;
        head->next = previous;
        previous = head;
        head = next;
    }
    return previous;
}
void judgePalindrome(C_NODE *head) {
    if (!head) { printf("true"); return; }
    C_NODE *slow = head, *fast = head;
    while (fast->next && fast->next->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    C_NODE *second = reverseHalf(slow->next);
    int palindrome = 1;
    for (C_NODE *a = head, *b = second; b; a = a->next, b = b->next) {
        if (a->data != b->data) palindrome = 0;
    }
    slow->next = reverseHalf(second);
    printf("%s", palindrome ? "true" : "false");
}
"""


def main():
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    baseline = json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:index.json"], check=True, capture_output=True).stdout)
    old_tasks = {(t["homework_id"], t["position"]): t for t in baseline["tasks"]}
    counts = {"expression": 0, "header_functions": 0, "multi_file": 0, "program": 0, "skipped": 0}
    for task in index["tasks"]:
        key = task["homework_id"], task["position"]
        old = old_tasks[key]
        directory = ROOT / task["directory"]
        if (directory / "skip.json").exists():
            counts["skipped"] += 1
            continue
        originals = {name: old_file(task["directory"], name) for name in old["answer_files"]}
        primary = next((code for name, code in originals.items() if name.endswith(".c") and not name.endswith("file2.c")), "")
        headers = [p for p in task["editable_paths"] if p.endswith(".h")]
        output = {}
        kind = "program"
        if key[0] == 4139803 and 1 <= key[1] <= 5:
            kind = "expression"
            output[headers[0]] = EXPRESSIONS[key[1]] + "\n"
        elif headers and key != (4139769, 11):
            kind = "header_functions"
            # All original standalone programs define their helper functions before main.
            match = re.search(r"\bint\s+main\s*\(", primary)
            assert match, key
            header = primary[:match.start()]
            if key == (4139790, 1):
                header = SELECTION
            elif key == (4139773, 7):
                header = PALINDROME
            elif key == (4139785, 2):
                header = header.replace("char name[100];", "char name[12];").replace("%99s", "%11s")
            elif key == (4139787, 3):
                header = header.replace("char *p;", "extern char *p;")
            elif key == (4139787, 2):
                header = header.replace("void reverseOrder(int *a, int n) {", "void reverseOrder(int *a, int n) {\n    if (n <= 1) return;")
            elif key == (4139793, 4):
                header = header.replace("int mystrlen(const char *s)", "int mystrlen(char *s)")
            elif key == (4139793, 1):
                start = header.index("void diceGame")
                random = header[header.index("static uint32_t state"):start]
                shim = "#ifdef _WIN32\n#include <stdint.h>\n#include <stdlib.h>\n" + random
                shim += "static int sample_rand(void) { return (int)random_next(); }\nstatic void sample_srand(unsigned int seed) { random_seed(seed); }\n#define rand sample_rand\n#define srand sample_srand\n#endif\n"
                write(directory / "harness/random_compat.h", shim)
                header = "#include <stdio.h>\n#include <stdlib.h>\n" + header[start:]
                header = header.replace("random_seed((unsigned)randSeed)", "srand((unsigned)randSeed)").replace("random_next()", "rand()")
            output[headers[0]] = header
            for path in task["editable_paths"]:
                if path.endswith(".c"):
                    output[path] = (directory / "starter" / path).read_text(encoding="utf-8")
        elif key == (4139769, 11):
            kind = "multi_file"
            for path in task["editable_paths"]:
                name = pathlib.PurePosixPath(path).name
                output[path] = primary if name == "file1.c" else originals["answer/" + name]
        else:
            assert len(task["editable_paths"]) == 1, key
            output[task["editable_paths"][0]] = primary
        for path in (directory / "answer").rglob("*"):
            if path.is_file():
                path.unlink()
        for path, content in output.items():
            write(directory / "answer" / path, content)
        # Remove empty old answer subdirectories only; never traverse outside this task.
        for path in sorted((directory / "answer").rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        submission = {"form": kind, "files": [{"answer": "answer/" + p, "platform_path": p} for p in output], "online_evaluated": False}
        write(directory / "submission.json", json.dumps(submission, ensure_ascii=False, indent=2) + "\n")
        lines = [f"# {task['title']}", "", "将下列答案文件的完整内容替换到对应的平台文件；文件名、路径和大小写保持一致。", "", "| 答案文件 | 平台文件 |", "| --- | --- |"]
        lines.extend(f"| [{pathlib.PurePosixPath(p).name}](answer/{p}) | `{p}` |" for p in output)
        if kind == "expression":
            lines += ["", "该 .h 文件就是单个表达式：不要添加 main、变量声明或末尾分号。可直接粘贴到题目 Begin-End 区域。"]
        if kind == "header_functions":
            lines += ["", "头文件仅包含所需函数、声明及依赖，不包含本地测试 main；本地入口在 harness/ 中。"]
        if key == (4139787, 2):
            lines += ["", "真实平台入口已在调用 reverseOrder 后输出数组，因此函数只负责反转，避免重复输出。"]
        if key == (4139773, 7):
            lines += ["", "C_NODE 由平台入口定义；答案不重复定义该类型。判断后恢复链表结构。"]
        lines += ["", "已做本地验证；没有提交头歌线上评测，隐藏测试与评分尚未验证。", ""]
        write(directory / "提交说明.md", "\n".join(lines))
        task["submission_form"] = kind
        task["answer_files"] = ["answer/" + p for p in output]
        write(directory / "task.json", json.dumps(task, ensure_ascii=False, indent=2) + "\n")
        counts[kind] += 1
    write(ROOT / "index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    print(counts)


if __name__ == "__main__":
    main()
