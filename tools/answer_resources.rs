//! Read explicitly named ancillary repository files needed for local homework tests.
use educoder_core::{EducoderClient, Session};
use serde_json::Value;
use std::path::Path;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root_arg = std::env::args()
        .nth(1)
        .ok_or("archive directory required")?;
    let root = Path::new(&root_arg);
    let index: Value = serde_json::from_slice(&std::fs::read(root.join("index.json"))?)?;
    let client = EducoderClient::new(
        Session::from_file(std::env::var_os("EDUCODER_COOKIES").ok_or("cookie path required")?)
            .await?,
    )?;
    for (hw, position, paths) in [
        (4139793, 1, vec!["src/Step1/step1_main.c"]),
        (4139782, 1, vec!["src/step1_1/test1.c"]),
        (4139782, 2, vec!["src/step2/Step2_main.c"]),
        (
            4139782,
            2,
            vec![
                "src/step2_1/test1.c",
                "src/step2_1/test2.c",
                "src/step2_1/test3.c",
            ],
        ),
        (
            4139776,
            1,
            vec!["src/step1/test1.txt", "src/step1/test2.txt"],
        ),
        (
            4139776,
            2,
            vec!["src/step2/test1.txt", "src/step2/test2.txt"],
        ),
        (
            4139776,
            3,
            vec!["src/step3/test1.txt", "src/step3/test2.txt"],
        ),
        (
            4139776,
            6,
            vec!["src/step6/matrix1.in", "src/step6/matrix2.in"],
        ),
    ] {
        if std::env::args().nth(2).is_some_and(|s| s != hw.to_string()) {
            continue;
        }
        let task = index["tasks"]
            .as_array()
            .unwrap()
            .iter()
            .find(|t| t["homework_id"] == hw && t["position"] == position)
            .ok_or("task missing")?;
        let sid = task["shixun"].as_str().unwrap();
        let instance = client
            .get_shixun(sid)
            .await?
            .myshixun_id
            .ok_or("instance missing")?;
        let games = client.get_my_challenges(&instance.to_string()).await?;
        let game = games
            .iter()
            .find(|g| g.position == position)
            .ok_or("game missing")?;
        for path in paths {
            match client.get_file_content(&game.identifier, path).await {
                Ok(file) => {
                    let dest = root
                        .join(task["directory"].as_str().unwrap())
                        .join("resources")
                        .join(path);
                    std::fs::create_dir_all(dest.parent().unwrap())?;
                    std::fs::write(dest, &file.content)?;
                    println!("{hw}/{position} {path}: {} bytes", file.content.len());
                }
                Err(e) => eprintln!("{hw}/{position} {path}: {e}"),
            }
        }
    }
    Ok(())
}
