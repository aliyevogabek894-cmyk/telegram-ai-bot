import os
import subprocess
from pathlib import Path

startup_dir = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
shortcut_path = str(startup_dir / "TelegramAIBot.lnk")

target = r"C:\Users\Teacher\Pictures\telegram AI\run_hidden.vbs"
working_dir = r"C:\Users\Teacher\Pictures\telegram AI"

powershell_cmd = f"$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('{shortcut_path}'); $s.TargetPath = '{target}'; $s.WorkingDirectory = '{working_dir}'; $s.Save()"

subprocess.run(["powershell", "-Command", powershell_cmd], check=True)
print("✅ AUTOSTART_SOZLANDI: Bot kompyuter yoqilganda avtomatik ishga tushadi!")
