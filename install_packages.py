import subprocess
import sys

def install(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

# List of packages to install
packages = [
    "PyQt5==5.15.9",
    "PyQt5-sip",
    "PyQt5-Qt5",
    "PyQtWebEngine==5.15.6",
    "python-dotenv",
    "bcrypt",
    "Pillow",
    "reportlab",
    "jinja2",
    "supabase",
    "storage3",
    "arabic-reshaper",
    "python-bidi"
]

print("Starting package installation...")
success_count = 0
failed_packages = []

for package in packages:
    if install(package):
        success_count += 1
    else:
        failed_packages.append(package)

print(f"\nInstallation Summary:")
print(f"✓ Successfully installed: {success_count}/{len(packages)} packages")
if failed_packages:
    print(f"✗ Failed packages: {', '.join(failed_packages)}")
else:
    print("🎉 All packages installed successfully!")

# Test PyQt5 import
try:
    import PyQt5
    print("✓ PyQt5 import test successful")
except ImportError as e:
    print(f"✗ PyQt5 import test failed: {e}")
