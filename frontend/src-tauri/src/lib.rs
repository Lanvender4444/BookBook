use tauri::Manager;
use std::fs;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .plugin(tauri_plugin_notification::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      
      // 读取根目录 config.json 中的后端端口，注入到前端
      let backend_port = fs::read_to_string("../config.json")
        .or_else(|_| fs::read_to_string("config.json"))
        .ok()
        .and_then(|s| serde_json::from_str::<serde_json::Value>(&s).ok())
        .and_then(|v| v.get("backend_port").and_then(|p| p.as_u64()))
        .unwrap_or(8000) as u32;
      
      if let Some(window) = app.get_webview_window("main") {
        let _ = window.eval(&format!("window.__BOOKBOOK_BACKEND_PORT__ = {};", backend_port));
      }
      
      let app_handle = app.handle().clone();
      std::thread::spawn(move || {
        let sidecar_command = app_handle.shell().sidecar("bookbook-backend").unwrap();
        let mut child = sidecar_command.spawn().expect("Failed to spawn sidecar");
        let mut stdout = child.stdout.take().unwrap();
        let mut stderr = child.stderr.take().unwrap();
        let mut buf = String::new();
        std::io::Read::read_to_string(&mut stdout, &mut buf).unwrap();
        if !buf.is_empty() {
          println!("[sidecar stdout] {}", buf);
        }
        let mut buf = String::new();
        std::io::Read::read_to_string(&mut stderr, &mut buf).unwrap();
        if !buf.is_empty() {
          eprintln!("[sidecar stderr] {}", buf);
        }
      });
      
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
