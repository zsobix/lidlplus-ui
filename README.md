# lidlplus-ui
<h3>The Lidl Plus app on Desktop (written in Python using GTK and libadwaita)</h3>


<img width="1163" height="708" alt="screenshot" src="https://github.com/user-attachments/assets/9cb6ef60-f60b-4727-ba66-b7a5a947db66" />

## Setup
Install Python 3 including pip

Clone this repo `git clone --recurse-submodules --remote-submodules https://github.com/Zsobix/lidlplus-ui`

Install all requirements `pip install -r requirements.txt`

Run `playwright install`

Install all dependencies that playwright requires


### Mac and Linux:
Install PyGObject, GTK, and libadwaita packages for your distro<sup><a href="https://pygobject.gnome.org/getting_started.html">[1]</a></sup>

Done!

### Windows
Follow the "Windows" part in <a href="https://pygobject.gnome.org/getting_started.html">this</a> guide.

Execute `pacman -Sy mingw-w64-ucrt-x86_64-libadwaita`

Since playwright doesn't work in Msys, you need to first run the `getrefreshtoken.py` file to get the refresh token.

On first login, instead of email and password, you need to give the refresh token instead.

Done!

## Usage

1. Run `ui.py`
2. Log in
3. ???
4. profit

## Legal Notice
This application is an open source project written in Python, which uses the API of the Lidl Plus application, owned by Lidl Stiftung & Co. KG. The application was created solely for educational purposes and is not affiliated with Lidl Stiftung & Co. KG. The creator of the application is not affiliated with Lidl Stiftung & Co. KG. in any way and does not derive any financial benefits from this project. All trademarks, trade names, and logos are the property of their respective owners. Users use the application at their own risk.
