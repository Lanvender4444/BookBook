use std::sync::Mutex;
use tauri::{Manager, RunEvent};
use tauri_plugin_shell::{process::CommandChild, ShellExt};

struct BackendProcess(Mutex<Option<CommandChild>>);

/// Kill the sidecar and its whole process tree.
/// PyInstaller --onefile spawns a child process, so on Windows we must use
/// `taskkill /T` to kill the tree — `child.kill()` alone leaves the real
/// Python process running and the port occupied.
fn kill_backend(child: CommandChild) {
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        let pid = child.pid();
        let _ = std::process::Command::new("taskkill")
            .args(["/F", "/T", "/PID", &pid.to_string()])
            .creation_flags(CREATE_NO_WINDOW)
            .status();
    }
    #[cfg(not(windows))]
    {
        let _ = child.kill();
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_log::Builder::default().build())
        .setup(|app| {
            // In dev mode the sidecar binary usually doesn't exist
            // (backend is started manually with `python main.py`),
            // so failure to spawn is only fatal in release builds.
            let child = match app
                .shell()
                .sidecar("backend")
                .and_then(|cmd| cmd.spawn())
            {
                Ok((_rx, child)) => {
                    log::info!("backend sidecar started, pid {}", child.pid());
                    Some(child)
                }
                Err(e) => {
                    if cfg!(debug_assertions) {
                        log::warn!(
                            "backend sidecar not started ({e}); dev mode: start it manually with `python main.py`"
                        );
                        None
                    } else {
                        return Err(format!("failed to start backend sidecar: {e}").into());
                    }
                }
            };
            app.manage(BackendProcess(Mutex::new(child)));
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let RunEvent::Exit = event {
                if let Some(state) = app_handle.try_state::<BackendProcess>() {
                    if let Some(child) = state.0.lock().unwrap().take() {
                        kill_backend(child);
                    }
                }
            }
        });
}
