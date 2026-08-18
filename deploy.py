import subprocess

def run_deployment_pipeline():
    commands = [
        "git init",
        "git add .",
        'git commit -m "Chani Core: Autonomous Multi-User Platform Deploy"',
        "git branch -M main"
    ]
    
    print("🚀 [Chani Core] กำลังเริ่มกระบวนการเตรียมโค้ดขึ้น GitHub...")
    for cmd in commands:
        try:
            res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"✅ สำเร็จ: {cmd}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ ข้ามหรือแจ้งเตือน [{cmd}]: {e.stderr.strip()}")
            
    print("✨ โค้ดพร้อมแล้ว! คุณสามารถพิมพ์คำสั่งเชื่อมต่อ GitHub Remote Repository ต่อได้ทันทีครับ")

if __name__ == "__main__":
    run_deployment_pipeline()
