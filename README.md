# Secure User Management System

A secure desktop application with a graphical installer for managing users, enforcing role-based access control, and storing credentials in an encrypted local database.

Developed using **PyQt6**, **ChaCha20 encryption**, and **Windows Registry** for integrity verification.

---

## Application Features

- Secure login with role-based access
- User creation with password policy enforcement
- Admin panel to manage users, roles, and status
- Encrypted local SQLite database (ChaCha20)
- System integrity check via digital signature in Windows Registry

---

## Installer Features

- PyQt6-based graphical installer
- Lets user select custom installation path
- Copies application files to selected location
- Shows progress and allows cancelation
- Generates RSA key pair and signs system info
- Stores signature and public key in Windows Registry
- Confirms successful installation at the end

---

## Project Structure

```
project/
├── gui.py                 # Main application GUI
├── db.py                  # Database access layer
└── installer/
    ├── installer.py       # Installer logic and GUI
    └── functions/
        ├── __init__.py
        ├── crypto_utils.py   # Encryption helpers (ChaCha20, RSA)
        ├── get_info.py       # System fingerprinting
        └── registry.py       # Registry access and signing logic
```

---

## Getting Started

### Running the Installer

1. **Compile the main application** (`gui.py`) using PyInstaller:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --icon "C:\...\icon.ico" --name "my_program" --add-data "C:\...\raccoon.jpg;." --add-data "C:\...\raccoon_simple.jpg;."  "C:\...\gui.py"
   ```
   This will generate `my_program.exe`.

2. **Compile the installer**:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --icon "C:\...\icon.ico" --name "my_program_install" --add-data "C:\...\my_program.exe;." --add-data "C:\...\install.jpg;."  "C:\...\installer.py"
   ```

3. **Run the installer**:
   ```bash
   ./dist/installer.exe
   ```
   - Choose an installation directory  
   - The compiled application (`my_program.exe`) will be installed there  
   - The system will be fingerprinted and digitally signed  
   - Upon success, a confirmation screen will appear

> Make sure `my_program.exe` is present during the installer build process. The program and installer will run without photos and icons, so compilation can be simplified.
<br> The installer binds the installation to current hardware. If system hardware changes significantly, the integrity check may fail.

---

## Running the Application

After installation launch the app:

```bash
my_program.exe
```

On first launch:
- You'll be asked for a **secret message** used to encrypt/decrypt the local DB.
- If `users_encrypted.bin` exists, it will be decrypted in memory.

### Login Procedure

- Select an existing user
- Enter password (3 tries max)
- Admins can:
  - View users
  - Change roles
  - Block/unblock accounts
  - Enforce password complexity rules

### Password Policy (Admin Configurable)

- Must include:
  - Latin characters
  - Cyrillic characters
  - Digits

---

## Author

**Maksym Kravchenko**, Student of the Kyiv Polytechnic Institute
