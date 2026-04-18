import os
from .ui import MyApp
import distro

def lidl_plus_run():
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_version('Adw', '1')
        from gi.repository import Gtk, Gdk, Adw, Gio, GdkPixbuf
    except:
        print("Couldn't find GTK/libadwaita, installing...")
        current_distro = distro.id()
        match current_distro:
            case "arch":
                os.system("sudo pacman -Sy cairo pkgconf gobject-introspection gtk4 libadwaita")
            case "opensuse":
                os.system("sudo zypper install cairo-devel pkg-config python3-devel gcc gobject-introspection-devel libadwaita")
            case "fedora":
                os.system("sudo dnf install gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4 libadwaita")
            case "ubuntu":
                os.system("sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 libadwaita-1")
            case "debian":
                os.system("sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 libadwaita-1")
            case "chromeos":
                print("You need to install https://github.com/chromebrew/chromebrew and run 'crew install gcc cairo gobject_introspection gtk4 libadwaita'")
                exit() 
            case "chrome":
                print("You need to install https://github.com/chromebrew/chromebrew and run 'crew install gcc cairo gobject_introspection gtk4 libadwaita'")
                exit()
            case "chromium":
                print("You need to install https://github.com/chromebrew/chromebrew and run 'crew install gcc cairo gobject_introspection gtk4 libadwaita'")
                exit()
            case "chromiumos":
                print("You need to install https://github.com/chromebrew/chromebrew and run 'crew install gcc cairo gobject_introspection gtk4 libadwaita'")
                exit()
            case "darwin":
                print("You need to install https://brew.sh and run 'brew install pygobject3 gtk4 libadwaita'")
                exit()
            case "macos":
                print("You need to install https://brew.sh and run 'brew install pygobject3 gtk4 libadwaita'")
                exit()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            browser.close()
    except:
        print("Couldn't find playwright browsers, trying to install.")
        os.system("playwright install chromium")

    app = MyApp(application_id="xyz.zsobix.lidlplusui")
    app.run()

def main():
    lidl_plus_run()

if __name__ == "__main__":
    main()