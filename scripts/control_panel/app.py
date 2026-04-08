import eel
import subprocess
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ai_process = None
gazebo_process = None

@eel.expose
def get_wifi_status():
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8', errors='ignore')
        if 'RotaTakipliOtonomSulamaAraci' in output:
            return {"connected": True}
        return {"connected": False, "ssid": "RotaTakipliOtonomSulamaAraci"}
    except Exception as e:
        return {"connected": False, "ssid": "RotaTakipliOtonomSulamaAraci", "error": str(e)}

@eel.expose
def close_app():
    sys.exit(0)

# AI SERVER
@eel.expose
def start_ai_server():
    global ai_process
    if ai_process is None:
        bat_path = os.path.join(project_root, 'deployment', 'pc', 'start_pc.bat')
        try:
            ai_process = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
        except Exception as e:
            print("Hata:", e)
            return False
    return True

@eel.expose
def stop_ai_server():
    global ai_process
    if ai_process:
        try:
            ai_process.terminate()
        except: pass
        ai_process = None
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq OtonomAraba*'], capture_output=True)
    return True

@eel.expose
def get_ai_status():
    global ai_process
    return ai_process is not None and ai_process.poll() is None

# GAZEBO SERVER
@eel.expose
def start_gazebo():
    global gazebo_process
    if gazebo_process is None:
        cmd = f'cd {os.path.join(project_root, "ros2_ws")} && ros2 launch plant_bot pc_sim_launch.py'
        try:
            gazebo_process = subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
            return True
        except Exception as e:
            print("Gazebo Hata:", e)
            return False
    return True

@eel.expose
def stop_gazebo():
    global gazebo_process
    subprocess.run(['taskkill', '/F', '/IM', 'gzserver.exe'], capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'ruby.exe'], capture_output=True)
    subprocess.run(['taskkill', '/F', '/IM', 'gzclient.exe'], capture_output=True)
    gazebo_process = None
    return True
    
@eel.expose
def open_gzclient():
    try:
        subprocess.Popen('start cmd /c "gzclient"', shell=True)
    except:
         pass

@eel.expose
def get_gazebo_status():
    global gazebo_process
    return gazebo_process is not None

if __name__ == '__main__':
    ui_folder = os.path.join(os.path.dirname(__file__), 'ui')
    eel.init(ui_folder)
    
    # Try Edge or Chrome in app mode
    try:
        eel.start('index.html', mode='edge', size=(1280, 720))
    except Exception:
        try:
            eel.start('index.html', mode='chrome', size=(1280, 720))
        except Exception:
            # Fallback to default browser
            eel.start('index.html', mode='default', size=(1280, 720))
