# core 导出工具

这里保留本次使用的 Rust 工具源码，网络访问、会话加载、限速和 Base64 解码均通过 Educoder++ 的 `educoder-core` 完成。

在 Educoder++ checkout 中，将需要使用的 `.rs` 文件复制到 `crates/core/examples/`，然后执行：

```powershell
$env:EDUCODER_COOKIES = 'D:\cookies.txt'
cargo run -p educoder-core --example archive_answers -- educoder-answer --allow-enter
cargo run -p educoder-core --example answer_resources -- educoder-answer
cargo run -p educoder-core --example audit_answer_contracts -- educoder-answer
```

`--allow-enter` 显式允许为尚未开始的作业建立个人实训实例，可能记录开始时间；本次已取得用户授权。不加该选项时只读取已有实例。工具从不保存远端代码或提交评测，不持久化登录会话。

导出按课程、作业分页、关卡读取；核对已列关卡数量，记录失败到 `index.json` 的 `issues`。已有完整 `task.json` 的关卡不覆盖题目及初始代码。重跑可继续补抓读取中断的作业；需要更新已存在题面时，应先自行备份并选定更新范围。

`answer_resources` 读取题面、主程序中明确指定的辅助文件；可追加作业 ID 参数，仅补读该作业，如 `educoder-answer 4139782`。辅助文件保持真实路径保存到 `resources/`。

`audit_answer_contracts` 只读获取函数和表达式题的真实平台主程序，保留在对应题目的 `harness/platform/`。已读取的入口会复用，不创建实例或提交代码。`platform-sources.json` 记录原始路径及来源，不保存个人实例标识。

`migrate_submission_forms.py` 是本次提交形式修正的一次性迁移工具。它从初始归档提交 `70fc848` 读取独立程序，把答案按真实平台文件路径整理为表达式、函数头文件或完整程序，并生成 `submission.json`。不要对已有手工更新的答案重新执行该一次性迁移；日常复验使用仓库根目录的 `verify.py`。

导出仅保存可公开展示的测试输入和预期输出，不保存隐藏测试、评测实际输出、个人实例标识、账号信息或提交上下文。可编辑文件来自用户授权的实训仓库，按原始字节保存。

本次使用的 core workspace 已运行 `cargo fmt --all -- --check`、`cargo check --workspace` 和 `cargo test --workspace`。常规测试使用模拟 HTTP 服务，没有执行真实平台提交。
