use std::sync::Mutex;
use tauri::{Manager, RunEvent};
use tauri_plugin_shell::{process::CommandChild, ShellExt};

/// 持有 backend sidecar 进程句柄，退出时 kill，避免残留进程占用端口/锁住 SQLite
struct BackendProcess(Mutex<Option<CommandChild>>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_log::Builder::default().build())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            // 启动前清理可能残留的旧 backend 进程，避免端口 18140/47833 被占用
            #[cfg(target_os = "windows")]
            {
                use std::os::windows::process::CommandExt;
                let _ = std::process::Command::new("taskkill")
                    .args(["/F", "/IM", "backend.exe"])
                    .creation_flags(0x0800_0000) // CREATE_NO_WINDOW
                    .output();
            }

            let sidecar = app
                .shell()
                .sidecar("backend")
                .expect("failed to find backend sidecar");
            let (_rx, child) = sidecar.spawn().expect("failed to start backend sidecar");
            app.manage(BackendProcess(Mutex::new(Some(child))));
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let RunEvent::Exit = event {
                if let Some(state) = app_handle.try_state::<BackendProcess>() {
                    if let Some(child) = state.0.lock().unwrap().take() {
                        let _ = child.kill();
                    }
                }
            }
        });
}
