# Lidl Plus on Desktop

A desktop UI for Lidl Plus, written in **Python** using **GTK** and **libadwaita**.

> This is an unofficial project and is not affiliated with Lidl.

<img width="1163" height="708" alt="screenshot" src="https://github.com/user-attachments/assets/9cb6ef60-f60b-4727-ba66-b7a5a947db66" />

## What you need

- **Python 3** + **pip**
- Git
- Platform dependencies for **GTK / libadwaita / PyGObject**
- Playwright browser dependencies

## Installation

> This only works on macOS/Linux only now because I gave up working with Windows.

### 1a) Download the flatpak package

Download and install the flatpak package from the **releases**

```bash
flatpak install xyz.zsobix.lidlplusui.flatpak
```

### 1b) Download from PyPI

```bash
pip install lidlplus-ui
```


## Running the app

### 2a) If you installed it with the flatpak package

Just run the desktop shortcut

Or run:

```bash
flatpak run xyz.zsobix.lidlplusui
```

The flatpak package has all dependencies included, so you **shouldn't** need to download anything.

### 2b) If you downloaded it from PyPI

```bash
lidlplus-ui
```
The script will attempt to automatically install all dependencies.

Then:
1. Log in
2. Use Lidl Plus on your desktop!!!

---

## Issues

If you have any problem with my project, just write in the issues tab!

## Legal notice

This is an open source project written in Python that interacts with the Lidl Plus API, which is owned by **Lidl Stiftung & Co. KG**.  
This project is provided for educational purposes. All trademarks and brand names belong to their respective owners.
