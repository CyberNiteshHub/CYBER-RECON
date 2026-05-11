import platform
import subprocess

def run(target):
    try:
        # OS Detection
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_flag = [] 
        
        if platform.system().lower() != 'windows':
            timeout_flag = ['-W', '2'] # 2 second timeout per packet on Linux
            
        # Command Construction
        command = ['ping', param, '4'] + timeout_flag + [target]
        
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return {"ok": True, "data": stdout}
        else:
            # Clean error message
            err = stderr if stderr else "Request timed out. Host is down or blocking ping."
            return {"ok": False, "error": err}
            
    except Exception as e:
        return {"ok": False, "error": f"Ping Execution Failed: {str(e)}"}