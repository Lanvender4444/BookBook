use tauri::Manager;
use tauri_plugin_shell::ShellExt;

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
