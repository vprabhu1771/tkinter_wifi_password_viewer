import subprocess
import platform
import tkinter as tk
from tkinter import messagebox


def get_wifi_profiles():
    """Retrieve Wi-Fi profiles based on the operating system."""
    os_name = platform.system()
    profiles = []
    
    try:
        if os_name == "Windows":
            result = subprocess.run(["netsh", "wlan", "show", "profile"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if "All User Profile" in line:
                    profiles.append(line.split(":")[1].strip())
        elif os_name == "Darwin":  # macOS
            result = subprocess.run(["/usr/sbin/networksetup", "-listallhardwareports"], capture_output=True, text=True)
            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.split("\n"):
                    if "Device:" in line:
                        interfaces.append(line.split(":")[1].strip())
                for interface in interfaces:
                    result = subprocess.run(
                        ["/usr/sbin/networksetup", "-listpreferredwirelessnetworks", interface],
                        capture_output=True, text=True
                    )
                    for line in result.stdout.split("\n"):
                        if "Preferred networks" not in line and line.strip():
                            profiles.append(line.strip())
        elif os_name == "Linux":
            result = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show"], capture_output=True, text=True)
            if result.returncode == 0:
                profiles = result.stdout.split("\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve Wi-Fi profiles: {e}")
    
    return [profile for profile in profiles if profile.strip()]


def get_wifi_password(profile_name):
    """Retrieve Wi-Fi password for the selected profile based on the OS."""
    os_name = platform.system()
    try:
        if os_name == "Windows":
            result = subprocess.run(
                ["netsh", "wlan", "show", "profile", profile_name, "key=clear"],
                capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "Key Content" in line:
                    return line.split(":")[1].strip()
            return "Password not found"
        elif os_name == "Darwin":  # macOS
            result = subprocess.run(
                ["security", "find-generic-password", "-D", "AirPort network password", "-a", profile_name, "-w"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Password not found or insufficient permissions"
        elif os_name == "Linux":
            result = subprocess.run(
                ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", profile_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Password not found"
    except Exception as e:
        return f"Error: {e}"


def show_password(event):
    """Display the password of the selected profile."""
    try:
        selected_profile = profile_listbox.get(profile_listbox.curselection())
        password = get_wifi_password(selected_profile)
        password_label.config(text=f"Password: {password}")
    except tk.TclError:
        pass  # Handle case where no profile is selected


# Create the main window
root = tk.Tk()
root.title("WiFi Password Manager")
root.geometry("400x300")

# Listbox to display Wi-Fi profiles
profile_listbox = tk.Listbox(root, width=50, height=15)
profile_listbox.pack(pady=10)
profile_listbox.bind("<<ListboxSelect>>", show_password)

# Label to display the password
password_label = tk.Label(root, text="Password: ", wraplength=300, justify="left")
password_label.pack(pady=10)

# Retrieve and display Wi-Fi profiles
profiles = get_wifi_profiles()
if profiles:
    for profile in profiles:
        profile_listbox.insert(tk.END, profile)
else:
    messagebox.showinfo("Info", "No Wi-Fi profiles found.")

# Run the Tkinter event loop
root.mainloop()
