//! Export authorized homework statements and public samples, never save or evaluate code.
use educoder_core::{
    EducoderClient, Session,
    models::{HomeworkKind, PageRequest},
};
use serde_json::{Value, json};
use std::{path::Path, time::Duration};

fn component(s: &str) -> String {
    s.chars()
        .map(|c| {
            if c.is_control() || "<>:\"/\\|?*%".contains(c) {
                format!("%{:04X}", c as u32)
            } else {
                c.to_string()
            }
        })
        .collect::<String>()
        .trim_end_matches([' ', '.'])
        .to_string()
}
fn write_json(path: &Path, value: &Value) -> Result<(), Box<dyn std::error::Error>> {
    std::fs::write(path, serde_json::to_vec_pretty(value)?)?;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let output = std::env::args().nth(1).ok_or("output directory required")?;
    let allow_enter = std::env::args().any(|a| a == "--allow-enter");
    let session = Session::from_file(
        std::env::var_os("EDUCODER_COOKIES").ok_or("EDUCODER_COOKIES required")?,
    )
    .await?;
    let client = EducoderClient::with_options(
        session,
        educoder_core::ClientOptions {
            timeout: Duration::from_secs(60),
            ..Default::default()
        },
    )?;
    let courses = client.get_courses().await?;
    let root = Path::new(&output);
    std::fs::create_dir_all(root)?;
    let mut entries = Vec::new();
    let mut issues = Vec::new();
    if courses
        .total
        .is_some_and(|n| n > courses.items.len() as u64)
    {
        issues.push(json!({"error":"course pagination incomplete"}));
    }
    for course in courses.items {
        let mut seen = std::collections::HashSet::new();
        for page in 1..=1000 {
            let homeworks = client
                .get_homeworks(
                    course.id,
                    HomeworkKind::Shixun,
                    PageRequest { page, limit: 50 },
                )
                .await?;
            if homeworks.items.is_empty() {
                break;
            }
            let total = homeworks.total;
            let mut new = 0;
            for hw in homeworks.items {
                if !seen.insert(hw.id) {
                    continue;
                }
                new += 1;
                println!("Homework {}: {}", hw.id, hw.name);
                let result: Result<(), Box<dyn std::error::Error>> = async {
                    let sid = hw.shixun_identifier.as_deref().ok_or("missing shixun")?;
                    let instance = if let Some(id) = hw.myshixun_identifier.clone() { id } else {
                        let shixun = client.get_shixun(sid).await?;
                        if let Some(id) = shixun.myshixun_id { id.to_string() } else {
                            if !allow_enter { return Err("no instance; explicit --allow-enter required".into()); }
                            let game = client.enter_shixun_for_homework(sid, hw.id).await?;
                            client.get_task(&game).await?.myshixun_identifier.ok_or("entered task has no instance identifier")?
                        }
                    };
                    let games = client.get_my_challenges(&instance).await?;
                    let challenges = client.get_challenges(sid).await?;
                    if games.len() != challenges.len() { issues.push(json!({"homework_id":hw.id,"error":"challenge count differs","listed":challenges.len(),"accessible":games.len()})); }
                    for game in games {
                        let rel = format!("{} [{}]/{} [{}]/{:02} {}", component(&course.name),course.id,component(&hw.name),hw.id,game.position,component(&game.name));
                        let dir = root.join(&rel);
                        if dir.join("task.json").exists() {
                            entries.push(serde_json::from_slice::<Value>(&std::fs::read(dir.join("task.json"))?)?);
                            continue;
                        }
                        let details = client.get_task_details(&game.identifier,hw.id).await?;
                        std::fs::create_dir_all(dir.join("starter"))?;
                        std::fs::write(dir.join("题目.md"), &details.task.description_markdown)?;
                        let tests: Vec<Value> = details.evaluation.tests.iter().filter(|t|t.public).map(|t|json!({"name":t.name,"input":t.input,"expected":t.expected})).collect();
                        write_json(&dir.join("samples.json"), &json!(tests))?;
                        for path in &details.task.editable_paths {
                            let file = client.get_file_content(&game.identifier,path).await?;
                            if path.contains("..") || path.starts_with(['/', '\\']) || path.contains(':') { return Err("unsafe repository path".into()); }
                            let dest = dir.join("starter").join(path);
                            std::fs::create_dir_all(dest.parent().unwrap())?;
                            std::fs::write(dest,file.content)?;
                        }
                        let entry = json!({"course":course.name,"course_id":course.id,"homework":hw.name,"homework_id":hw.id,"shixun":sid,"position":game.position,"title":details.task.title,"listed_title":game.name,"directory":rel,"editable_paths":details.task.editable_paths,"public_samples":tests.len(),"status":"pending"});
                        write_json(&dir.join("task.json"), &entry)?;
                        println!("  {:02} {} ({} public samples)",game.position,game.name,tests.len());
                        entries.push(entry);
                        write_json(&root.join("index.json"), &json!({"tasks":entries,"issues":issues}))?;
                    }
                    Ok(())
                }.await;
                if let Err(e) = result {
                    eprintln!("Homework {}: {}", hw.id, e);
                    issues.push(json!({"homework_id":hw.id,"error":e.to_string()}));
                }
                write_json(
                    &root.join("index.json"),
                    &json!({"tasks":entries,"issues":issues}),
                )?;
            }
            if new == 0 || total.is_some_and(|n| seen.len() as u64 >= n) {
                break;
            }
        }
    }
    println!("Exported {} tasks; {} issues", entries.len(), issues.len());
    Ok(())
}
