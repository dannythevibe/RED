from system.red_system import SystemController

sys = SystemController()

print("Testing Universal App Control...")
apps_to_test = ["notepad", "calc", "cmd"]

for app in apps_to_test:
    result = sys.open_app(app)
    print(f"App: {app} | Success: {result}")
