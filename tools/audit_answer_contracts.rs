//! Read-only audit of platform entry points for header/expression homework answers.
use educoder_core::{EducoderClient, Session};
use serde_json::{Value, json};
use std::{collections::HashMap, path::Path};

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
    let mut games = HashMap::new();
    for t in index["tasks"].as_array().unwrap() {
        let paths: Vec<&str> = t["editable_paths"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(Value::as_str)
            .collect();
        if !paths.iter().any(|p| p.ends_with(".h"))
            || t["homework_id"] == 4139769 && t["position"] == 11
        {
            continue;
        }
        let dir = root.join(t["directory"].as_str().unwrap());
        std::fs::create_dir_all(dir.join("harness"))?;
        if dir.join("harness/platform-sources.json").exists() {
            let previous: Value =
                serde_json::from_slice(&std::fs::read(dir.join("harness/platform-sources.json"))?)?;
            if previous.as_array().is_some_and(|v| !v.is_empty()) {
                continue;
            }
        }
        let sid = t["shixun"].as_str().unwrap();
        if !games.contains_key(sid) {
            let instance = client
                .get_shixun(sid)
                .await?
                .myshixun_id
                .ok_or("existing instance missing")?;
            games.insert(
                sid.to_string(),
                client.get_my_challenges(&instance.to_string()).await?,
            );
        }
        let game = games[sid]
            .iter()
            .find(|g| u64::from(g.position) == t["position"].as_u64().unwrap())
            .ok_or("game missing")?;
        let mut candidates = Vec::new();
        for path in &paths {
            if path.ends_with(".c") {
                candidates.push(path.to_string());
            }
        }
        if candidates.is_empty() {
            for path in &paths {
                let stem = path.strip_suffix(".h").unwrap();
                let main = if let Some(prefix) = stem
                    .strip_suffix("_stu")
                    .or_else(|| stem.strip_suffix("_func"))
                {
                    format!("{prefix}_main.c")
                } else {
                    format!("{}/main.c", path.rsplit_once('/').unwrap().0)
                };
                candidates.push(main);
            }
        }
        if t["homework_id"] == 4139785 {
            candidates = vec!["src/step2/Step2_main.c".into()];
        }
        let mut records = Vec::new();
        for path in candidates {
            let existing = dir.join("starter").join(&path);
            let bytes = if existing.exists() {
                std::fs::read(existing)?
            } else {
                match client.get_file_content(&game.identifier, &path).await {
                    Ok(f) if !f.content.is_empty() => f.content,
                    Ok(_) => {
                        eprintln!("empty {path}");
                        continue;
                    }
                    Err(e) => {
                        eprintln!("{} {} {path}: {e}", t["homework_id"], t["position"]);
                        continue;
                    }
                }
            };
            let dest = dir.join("harness/platform").join(&path);
            std::fs::create_dir_all(dest.parent().unwrap())?;
            std::fs::write(&dest, &bytes)?;
            records.push(json!({"path":path,"source":"platform_repository","bytes":bytes.len()}));
            println!(
                "{} {} {path}: {} bytes",
                t["homework_id"],
                t["position"],
                bytes.len()
            );
        }
        std::fs::write(
            dir.join("harness/platform-sources.json"),
            serde_json::to_vec_pretty(&records)?,
        )?;
    }
    Ok(())
}
