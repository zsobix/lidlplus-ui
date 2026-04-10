# Lidl Plus on Desktop

A desktop UI for Lidl Plus, written in **Python** using **GTK** and **libadwaita**.

> This is an unofficial project and is not affiliated with Lidl.

<img width="1163" height="708" alt="screenshot" src="https://github.com/user-attachments/assets/9cb6ef60-f60b-4727-ba66-b7a5a947db66" />

## What you need

- **Python 3** + **pip**
- Git
- Platform dependencies for **GTK / libadwaita / PyGObject**
- Playwright browser dependencies (macOS/Linux)

## Installation

### 1) Download from PyPI

```bash
pip install lidlplus-ui
```

---

## macOS / Linux setup

### 2) Install Playwright browser(s)

```bash
playwright install
```

### 3) Install system packages

You must install **PyGObject**, **GTK**, and **libadwaita** for your distribution.

- See PyGObject’s official “Getting Started” guide: https://pygobject.gnome.org/getting_started.html

After that, you’re ready to run the app.

---

## Windows setup (MSYS2)

### 2) Install GTK/libadwaita via pacman

Follow the **Windows** section of the PyGObject guide first:
https://pygobject.gnome.org/getting_started.html

Then install libadwaita:

```bash
pacman -Sy mingw-w64-ucrt-x86_64-libadwaita
```

### 3) Playwright note (important)

Playwright does **not** work in MSYS2, so login works differently on Windows:

1. Run this script to obtain a refresh token:
   ```bash
   lidlplus-ui auth
   ```
2. On the first login in the UI, enter the **refresh token** instead of email/password.

---

## Running the app

```bash
lidlplus-ui
```

Then:
1. Launch the app
2. Log in
3. Use Lidl Plus on your desktop

---

## Legal notice

This is an open source project written in Python that interacts with the Lidl Plus API, which is owned by **Lidl Stiftung & Co. KG**.  
This project is provided for educational purposes. All trademarks and brand names belong to their respective owners.
