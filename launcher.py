import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Initialize CPU limits early to prevent high CPU usage
try:
    from utils.cpu_manager import initialize_cpu_limits
    
    # Check for --use-all-cores flag
    if "--use-all-cores" in sys.argv:
        import psutil
        total_cores = psutil.cpu_count() or 4
        initialize_cpu_limits(max_cores=total_cores, max_threads=total_cores)
        print(f"Using all {total_cores} CPU cores (--use-all-cores flag)")
    else:
        initialize_cpu_limits()  # Uses dynamic calculation: total_cores / 4
except Exception as e:
    print(f"Warning: Could not initialize CPU limits: {e}")

# This is temporary as pystray / pillow is required for the minimize to tray function, some users may not rerun setup.
# It will be removed in the next release
def ensure_pystray():
    """Check if pystray is installed and install it if not"""
    try:
        import pystray
        return True
    except ImportError:
        import subprocess
        
        # Use runtime python to install pystray and Pillow (required dependency)
        python_exe = os.path.join(current_dir, "runtime", "python.exe")
        
        try:
            # Install pystray and Pillow
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", "pystray", "Pillow"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"Failed to install pystray: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error installing pystray: {e}")
            return False

if __name__ == "__main__":
    ensure_pystray()
    
    # Check for --hidden flag to restart without console
    if "--hidden" in sys.argv and "--restarted" not in sys.argv:
        import subprocess
        # Restart the script without a console window
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen([sys.executable, __file__, "--hidden", "--restarted"], 
                        creationflags=CREATE_NO_WINDOW)
        sys.exit(0)
    
    from gui.gui import GUI
    GUI()
