"""Interface regressions that public stdin/stdout samples cannot detect."""
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
TASKS = {(t["homework_id"], t["position"]): t for t in json.loads((ROOT / "index.json").read_text(encoding="utf-8"))["tasks"]}


def header(homework, position):
    task = TASKS[homework, position]
    path = next(p for p in task["editable_paths"] if p.endswith(".h"))
    return (ROOT / task["directory"] / "answer" / path).as_posix()


class SubmissionContracts(unittest.TestCase):
    def compile_and_run(self, source, expected=b""):
        build = ROOT / ".build"
        build.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="interface-", dir=build) as temporary:
            work = pathlib.Path(temporary)
            code, exe = work / "contract.c", work / "contract.exe"
            code.write_bytes(source.encode("utf-8"))
            result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-finput-charset=UTF-8", str(code), "-o", str(exe)], capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            run = subprocess.run([str(exe)], capture_output=True, timeout=5)
            self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(run.stdout, expected)

    def test_palindrome_preserves_chain_and_initializes_empty_head(self):
        self.compile_and_run(f'''#include <assert.h>
#include <string.h>
typedef struct c_node {{char data; struct c_node *next;}} C_NODE;
#include "{header(4139773, 7)}"
int main(void) {{
    C_NODE sentinel = {{0, 0}}, *head = &sentinel;
    char empty[] = "", text[] = "abba", other[] = "abc";
    createLinkList(&head, empty); assert(head == 0);
    judgePalindrome(head);
    createLinkList(&head, text);
    judgePalindrome(head); judgePalindrome(head);
    int i = 0;
    for (C_NODE *p = head; p; p = p->next) assert(p->data == text[i++]);
    assert(i == 4);
    while (head) {{C_NODE *next = head->next; free(head); head = next;}}
    createLinkList(&head, other); judgePalindrome(head);
    while (head) {{C_NODE *next = head->next; free(head); head = next;}}
    return 0;
}}
''', b"truetruetruefalse")

    def test_main0_uses_external_pointer_and_does_not_print(self):
        self.compile_and_run(f'''#include <assert.h>
#include "{header(4139787, 3)}"
char *p;
int main(void) {{
    char *args[] = {{"strcat", "abc", "def", "ghi"}};
    assert(main0(4, args) == 0);
    assert(strcmp(p, "abcdefghi") == 0); free(p);
    assert(main0(0, NULL) == 0); assert(p[0] == 0); free(p);
    return 0;
}}
''')

    def test_student_layout_matches_template(self):
        self.compile_and_run(f'''#include "{header(4139785, 2)}"
_Static_assert(sizeof(((struct student *)0)->name) == 12, "platform name field must remain 12 bytes");
int main(void) {{ return 0; }}
''')

    def test_empty_and_single_element_pointer_arrays(self):
        self.compile_and_run(f'''#include <assert.h>
#include "{header(4139787, 1)}"
#include "{header(4139787, 2)}"
int main(void) {{
    int a[] = {{42, 99}};
    bubble_sort(a, 0); reverseOrder(a, 0);
    bubble_sort(a, 1); reverseOrder(a, 1);
    assert(a[0] == 42 && a[1] == 99);
    reverseOrder(a, 2); assert(a[0] == 99 && a[1] == 42);
    return 0;
}}
''')


if __name__ == "__main__":
    unittest.main()
