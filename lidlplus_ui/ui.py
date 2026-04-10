import sys
import gi
import lidlplus_api
import requests
import os
import json
import time
import qrcode
import webbrowser
import datetime

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GdkPixbuf

# Import css
css_provider = Gtk.CssProvider()
css_provider.load_from_string("""
.button {
    border-radius: 15px;
    margin: 15px;
}
.picture {
    border-radius: 15px;
    margin: 5px;
}
.login-boxes {
    margin: 25px;
}
.text {
    margin: 5px;
    text-align: center;
}
.home {
    margin-left: 1px;
    margin-right: 1px;
}
.schedule {
    margin: 5px;
}
.settings {
    margin: 5px;
    margin-left: 20px;
    margin-right: 20px;
}
.buttontext {
    margin-right: 15px;
    margin-left: auto;
    align-items: flex-end;
    float: right;
    display: flex;
    justify-content: flex-end;
}
.description {
    text-align: center;
}""")
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initalize
        self.logged_in = False
        self.store = ""

        self.set_default_size(600, 250)
        self.set_title("Lidl Plus on Desktop")
        self.titlebar = Gtk.HeaderBar()
        self.set_titlebar(self.titlebar)
        
        self.home()
        
        # Setup hamburger menu
        action = Gio.SimpleAction.new("coupons", None)
        action.connect("activate", self.coupons)
        home = Gio.SimpleAction.new("home", None)
        home.connect("activate", self.home)
        offers = Gio.SimpleAction.new("offers", None)
        offers.connect("activate", self.offers)
        brochures = Gio.SimpleAction.new("brochures", None)
        brochures.connect("activate", self.brochures)
        settings = Gio.SimpleAction.new("settings", None)
        settings.connect("activate", self.settings)
        logout = Gio.SimpleAction.new("logout", None)
        logout.connect("activate", self.logout)

        self.add_action(action)
        self.add_action(home)
        self.add_action(offers)
        self.add_action(brochures)
        self.add_action(settings)
        self.add_action(logout)

        menu = Gio.Menu.new()

        menu.append("Home", "win.home")
        menu.append("Coupons", "win.coupons")
        menu.append("Offers", "win.offers")
        menu.append("Brochures", "win.brochures")
        menu.append("Settings", "win.settings")
        menu.append("Logout", "win.logout")

        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(menu)

        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")

        self.titlebar.pack_start(self.hamburger)

        self.homebutton = Gtk.Button()
        self.homebutton.connect("clicked", self.home)
        self.homebutton.set_icon_name("go-home-symbolic")

        self.titlebar.pack_start(self.homebutton)

        # Create a button for redeeming the purchase lottery
        self.purchaseLotterybutton = Gtk.Button()
        self.purchaseLotterybutton.connect("clicked", self.purchaseLottery)
        #self.purchaseLotterybutton.set_icon_name("package-x-generic-symbolic")
        self.purchaseLotterybutton.set_icon_name("auth-smartcard-symbolic")
        self.titlebar.pack_start(self.purchaseLotterybutton)

    def logout(self, action="", param=""):
        # Logout procedure
        if self.logged_in:
            os.remove("login.json")
            self.logged_in = False
            self.home()

    def coupons(self, action="", param=""):
        if self.logged_in:
            scrollwin = Gtk.ScrolledWindow.new()
            self.set_child(scrollwin)
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.displaybox)
            self.label = Gtk.Label()
            self.displaybox.append(self.label)
            activecoupons = self.lidl.activecoupons_count(self.store)["activeCount"]
            self.label.set_markup(f'<span size="larger" weight="bold">Coupons\nActive coupons count: {activecoupons}</span>')
            self.label.set_css_classes(["text"])
            coupons = self.lidl.coupons(self.store)["sections"][0]["promotions"]
            for coupon in coupons:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.displaybox.append(activate)
                activate.connect("clicked", self.details)
                centerbox = Gtk.CenterBox()
                activate.set_child(centerbox)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.displaybox.append(box)
                centerbox.set_start_widget(box)
                #img = Gio.File.new_for_uri(coupon["image"]["url"])
                #img2 = GdkPixbuf.Pixbuf.new_from_stream(img.read(cancellable=None))
                #image = Gtk.Picture().new_for_pixbuf(img2)
                img = requests.get(coupon["image"]["url"])
                with open(f"{coupon["id"]}.jpg", "wb") as w:
                    w.write(img.content)
                image = Gtk.Picture().new_for_filename(f"{coupon["id"]}.jpg")
                image.set_css_classes(["picture"])
                box.append(image)

                box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box.append(box2)
                today = datetime.datetime.now(datetime.timezone.utc)
                try:
                    expirydate = datetime.datetime.strptime(coupon["validity"]["end"], "%Y-%m-%dT%H:%M:%S.%f%z")
                except:
                    expirydate = datetime.datetime.strptime(f"{coupon["validity"]["end"]}+0100", "%Y-%m-%dT%H:%M:%SZ%z")
                expirydate = expirydate - today
                expirydate = expirydate.days
                name = Gtk.Label()
                name.set_markup(f'<span size="1%">{coupon["id"]}div{coupon["isActivated"]}div{expirydate}div</span><span size="larger">{coupon["title"]}\n</span><span>{coupon["discount"]["title"]}, {coupon["discount"]["description"]}</span>')
                name.set_css_classes(["text"])
                box2.append(name)

                box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                centerbox.set_end_widget(box3)

                activatebut = Gtk.Button(label="Activate/Deactivate")
                box3.append(activatebut)

                name2 = Gtk.Label()
                if not coupon["isActivated"]:
                    name2.set_markup('<span size="1%">div{coupon["id"]}div{coupon["isActivated"]}</span><span size="x-large">Activate</span>')
                else:
                    name2.set_markup('<span size="1%">div{coupon["id"]}div{coupon["isActivated"]}</span><span size="x-large">Deactivate</span>')
                activatebut.set_child(name2)
                #box3.append(name2)
                #activatebut = Gtk.Button(label="Activate/Deactivate")
                #box3.append(activatebut)
                #set_id = Gtk.Label()
                #if bool(coupon["isActivated"]):
                #    set_id.set_markup(f'<span size="1%">div{coupon["id"]}div{coupon["isActivated"]}</span><span>Deactivate</span>')
                #if not bool(coupon["isActivated"]):
                #    set_id.set_markup(f'<span size="1%">div{coupon["id"]}div{coupon["isActivated"]}</span><span>Activate</span>')
                ##set_id.set_visible(False)
                #activate.set_child(set_id)
                #activate.connect("clicked", self.toggle)

    def details(self, action):
        box = action.get_child().get_start_widget()
        box2 = box.get_first_child().get_next_sibling()
        text = box2.get_first_child().get_text()
        info = text.split("div")
        self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.displaybox)

        home_button = Gtk.Button(label="Back")
        home_button.connect("clicked", self.coupons)
        home_button.set_css_classes(["button"])
        self.displaybox.append(home_button)

        image = Gtk.Picture().new_for_filename(f"{info[0]}.jpg")
        image.set_css_classes(["picture"])
        self.displaybox.append(image)

        title = Gtk.Label()
        title.set_markup(f'<span size="200%">{info[3]}\n{info[2]} day(s) left</span>')
        title.set_css_classes(["description"])
        self.displaybox.append(title)

        button = Gtk.Button(label="test")
        button.set_css_classes(['button'])
        button.connect("clicked", self.toggle)
        self.displaybox.append(button)

        buttontext = Gtk.Label()
        button.set_child(buttontext)
        if info[1] == "False":
            buttontext.set_markup(f'<span size="1%">{info[0]}div{info[1]}div</span><span size="200%">Activate</span>')
        else:
            buttontext.set_markup(f'<span size="1%">{info[0]}div{info[1]}div</span><span size="200%">Deactivate</span>')

    def toggle(self, action):
        label = action.get_child()
        info = label.get_text().split("div")
        isActivated = info[1]
        coupon_id = info[0]
        if isActivated == "True":
            if self.lidl.deactivate_coupon(coupon_id=coupon_id):
                self.coupons()
        else:
            if self.lidl.activate_coupon(coupon_id=coupon_id):
                self.coupons()


    def offers(self, action="", param=""):
         if self.logged_in:
            scrollwin = Gtk.ScrolledWindow.new()
            self.set_child(scrollwin)
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.displaybox)
            self.label = Gtk.Label()
            self.displaybox.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Offers</span>')
            self.label.set_css_classes(["text"])
            offers = self.lidl.offers(self.store)["offers"]
            for offer in offers:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.displaybox.append(activate)
                #activate.connect("clicked", self.details)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.displaybox.append(box)
                activate.set_child(box)
                #img = requests.get(offer["imageUrl"])
                #with open(f"{offer["id"]}.jpg", "wb") as w:
                #    w.write(img.content)
                #image = Gtk.Picture().new_for_filename(f"{offer["id"]}.jpg")
                img = Gio.File.new_for_uri(offer["imageUrl"])
                img2 = GdkPixbuf.Pixbuf.new_from_stream(img.read(cancellable=None))
                image = Gtk.Picture().new_for_pixbuf(img2)
                image.set_css_classes(["picture"])
                box.append(image)

                box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box.append(box2)

                name = Gtk.Label()
                if offer["brand"]:
                    name.set_markup(f'<span size="larger">{offer["brand"].replace("&", "and")} {offer["title"]}\n</span><span>{offer["priceBox"]["discountMessage"]}</span>')
                else:
                    name.set_markup(f'<span size="larger">{offer["title"]}\n</span><span>{offer["priceBox"]["discountMessage"]}</span>')
                name.set_css_classes(["text"])
                box2.append(name)

                box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box2.append(box3)

    def brochures(self, action="", param=""):
        if self.logged_in:
            scrollwin = Gtk.ScrolledWindow.new()
            self.set_child(scrollwin)
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.displaybox)
            self.label = Gtk.Label()
            self.displaybox.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Coupons</span>')
            self.label.set_css_classes(["text"])
            brochures = self.lidl.brochures(self.store)[0]["flyers"]
            for brochure in brochures:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.displaybox.append(activate)
                activate.connect("clicked", self.brochuredetails)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.displaybox.append(box)
                activate.set_child(box)
                img = Gio.File.new_for_uri(brochure["thumbnailUrl"])
                img2 = GdkPixbuf.Pixbuf.new_from_stream(img.read(cancellable=None))
                image = Gtk.Picture().new_for_pixbuf(img2)
                #img = requests.get(brochure["thumbnailUrl"])
                #with open(f"{brochure["id"]}.jpg", "wb") as w:
                #    w.write(img.content)
                #image = Gtk.Picture().new_for_filename(f"{coupon["id"]}.jpg")
                image.set_css_classes(["picture"])
                box.append(image)

                box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box.append(box2)

                name = Gtk.Label()
                name.set_markup(f'<span size="1%">{brochure["viewUrl"]}div</span><span size="larger">{brochure["title"]}\n</span><span>  {brochure["name"]}</span>')
                name.set_css_classes(["text"])
                box2.append(name)

                box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box2.append(box3)

    def brochuredetails(self, action):
        box = action.get_child()
        box2 = box.get_first_child().get_next_sibling()
        text = box2.get_first_child().get_text()
        info = text.split("div")
        webbrowser.open(info[0])

    def login(self, action):
        if not os.path.exists("login.json"):
            if self.refreshtokenentry.get_text() != "":
                self.lidl = lidlplus_api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper(), refresh_token=self.refreshtokenentry.get_text())
                self.store = requests.get(f"https://stores.lidlplus.com/api/v4/{self.country}").json()[0]["storeKey"]
                with open("login.json", "w") as login:
                    login.write(json.dumps({"refresh_token": self.lidl._refresh_token, "country": self.country, "store": self.store}))
            else:
                self.lidl = lidlplus_api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper())
                self.lidl.login(email=self.usernameentry.get_text(), password=self.passwordentry.get_text())
                self.store = requests.get(f"https://stores.lidlplus.com/api/v4/{self.country}").json()[0]["storeKey"]
                with open("login.json", "w") as login:
                    login.write(json.dumps({"refresh_token": self.lidl._refresh_token, "country": self.country, "store": self.store}))
        else:
            with open("login.json", "r") as login:
                loader = json.loads(login.read())
                refresh_token = loader["refresh_token"]
            self.lidl = lidlplus_api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper(), refresh_token=refresh_token)
        #print(self.usernameentry.get_text())
        #print(self.passwordentry.get_text())
        self.logged_in = True
        self.home()
    def home(self, action="", param=""):
        self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.displaybox)
        self.displaybox.set_css_classes(["home"])
        self.label = Gtk.Label()
        self.label.set_css_classes(["text"])
        self.displaybox.append(self.label)
        if self.logged_in:
            self.centerbox = Gtk.CenterBox()
            self.set_child(self.centerbox)
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.centerbox.set_center_widget(self.displaybox)
            #if len(self.lidl.home(self.store)["purchaseLottery"]) == 0:
            #    self.label.set_markup('<span size="larger" weight="bold">Home</span>')
            #else:
            #    self.label.set_markup(f'<span size="larger" weight="bold">Home\nYou have a scratch card to redeem!</span>')
            
            schedulebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.displaybox.append(schedulebox)
            schedule = Gtk.Label()
            schedulebox.append(schedule)
            store_schedule = self.lidl.store_schedule(self.store)
            if store_schedule['isOpen'] == "False":
                schedule.set_markup(f'<span weight="bold" size="large">Favourite store:\n</span><span size="large">{self.lidl.store_details(self.store)[0]["name"]} (currently <b>closed</b>), \nopen from: {store_schedule["openingHours"][0]["from"]}-{store_schedule["openingHours"][0]["to"]}</span>')
            else:
                schedule.set_markup(f'<span weight="bold" size="large">Favourite store:\n</span><span size="large">{self.lidl.store_details(self.store)[0]["name"]} (currently <b>open</b>), \nopen from: <b>{store_schedule["openingHours"][0]["from"]}-{store_schedule["openingHours"][0]["to"]}</b></span>')
            schedule.set_css_classes(["schedule"])
            
            
            # grid
            grid = Gtk.Grid()
            self.displaybox.append(grid)

            # qr code
            qrbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            grid.attach(qrbox, column=0, row=0, width=1, height=1)
            qr = qrcode.make(self.lidl.loyalty_id)
            qr.save("loyaltyId.png")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename='loyaltyId.png', width=290, height=290, preserve_aspect_ratio=False)
            qrimg = Gtk.Picture().new_for_pixbuf(pixbuf)
            qrimg.set_css_classes(["picture"])
            qrbox.append(qrimg)

            # buttons
            buttonsbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            grid.attach(buttonsbox, column=1, row=0, width=5, height=1)

            couponbutton = Gtk.Button(label="coupons")
            couponbutton.set_css_classes(['button'])
            couponbutton.connect("clicked", self.coupons)
            buttonsbox.append(couponbutton)

            couponlabel = Gtk.Label()
            couponlabel.set_markup('<span size="x-large">                         Coupons                         </span>')
            couponbutton.set_child(couponlabel)

            offerbutton = Gtk.Button(label="offers")
            offerbutton.set_css_classes(['button'])
            offerbutton.connect("clicked", self.offers)
            buttonsbox.append(offerbutton)

            offerlabel = Gtk.Label()
            offerlabel.set_markup('<span size="x-large">                          Offers                          </span>')
            offerbutton.set_child(offerlabel)

            brochuresbutton = Gtk.Button(label="brochures")
            brochuresbutton.set_css_classes(['button'])
            brochuresbutton.connect("clicked", self.brochures)
            buttonsbox.append(brochuresbutton)

            brochureslabel = Gtk.Label()
            brochureslabel.set_markup('<span size="x-large">                           Brochures                            </span>')
            brochuresbutton.set_child(brochureslabel)

            settingsbutton = Gtk.Button(label="settings")
            settingsbutton.set_css_classes(['button'])
            settingsbutton.connect("clicked", self.settings)
            buttonsbox.append(settingsbutton)

            settingslabel = Gtk.Label()
            settingslabel.set_markup('<span size="x-large">                           Settings                            </span>')
            settingsbutton.set_child(settingslabel)
            

            logoutbutton = Gtk.Button(label="logout")
            logoutbutton.set_css_classes(['button'])
            logoutbutton.connect("clicked", self.logout)
            buttonsbox.append(logoutbutton)

            logoutlabel = Gtk.Label()
            logoutlabel.set_markup('<span size="x-large">                           Logout                            </span>')
            logoutbutton.set_child(logoutlabel)

            if len(self.lidl.home(self.store)["purchaseLottery"]) == 0:
                self.label.set_markup('<span size="larger" weight="bold">Home</span>')
            else:
                self.label.set_markup(f'<span size="larger" weight="bold">Home\nYou have a scratch card to redeem!</span>')
                lotterybutton = Gtk.Button(label="lottery")
                lotterybutton.set_css_classes(['button'])
                lotterybutton.connect("clicked", self.purchaseLottery)
                buttonsbox.append(lotterybutton)

                lotterylabel = Gtk.Label()
                lotterylabel.set_markup('<span size="x-large">                           Redeem Purchase Lottery                            </span>')
                lotterybutton.set_child(lotterylabel)

        if not self.logged_in:
            if not os.path.exists("login.json"):
                passwordbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.displaybox.append(passwordbox)
                passwordbox.set_css_classes(["login-boxes"])

                usernamebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                passwordbox.append(usernamebox)
                usernamebox.set_css_classes(["login-boxes"])

                self.usernameentry = Gtk.Entry()
                usernamebox.append(self.usernameentry)

                usernamelabel = Gtk.Label()
                usernamelabel.set_markup('<span size="medium">Email</span>')
                usernamebox.append(usernamelabel)

                self.passwordentry = Gtk.PasswordEntry()
                passwordbox.append(self.passwordentry)
                self.passwordentry.set_show_peek_icon(True)

                passwordlabel = Gtk.Label()
                passwordlabel.set_markup('<span size="medium">Password</span>')
                passwordbox.append(passwordlabel)

                countrybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                passwordbox.append(countrybox)
                countrybox.set_css_classes(["login-boxes"])

                countrydd = Gtk.DropDown()
                countrydd.connect("notify::selected-item", self.set_country)
                countrybox.append(countrydd)

                strings = Gtk.StringList()
                countrydd.props.model = strings
                countries = requests.get("https://appgateway.lidlplus.com/configurationapp/v3/countries").json()
                items = ""
                for country in countries:
                    items = items+" "+country["id"]
                items = items.split()

                for item in items:
                    strings.append(item)

                countrylabel = Gtk.Label()
                countrylabel.set_markup('<span size="medium">Country</span>')
                countrybox.append(countrylabel)

                refreshtokenbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                countrybox.append(refreshtokenbox)
                refreshtokenbox.set_css_classes(["login-boxes"])

                self.refreshtokenentry = Gtk.Entry()
                refreshtokenbox.append(self.refreshtokenentry)

                refreshtokenlabel = Gtk.Label()
                refreshtokenlabel.set_markup('<span size="medium">Refresh Token (optional)</span>')
                refreshtokenbox.append(refreshtokenlabel)

                buttonbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                countrybox.append(buttonbox)
                buttonbox.set_css_classes(["login-boxes"])

                button = Gtk.Button(label="Login")
                buttonbox.append(button)
                button.connect("clicked", self.login)

                login_button_label = Gtk.Label()
                login_button_label.set_markup('<span size="large">Login</span>')
                button.set_child(login_button_label)
            else:
                with open("login.json", "r") as login:
                    loader = json.loads(login.read())
                    self.refresh_token = loader["refresh_token"]
                    self.country = loader["country"]
                    self.store = loader["store"]
                self.lidl = lidlplus_api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper(), refresh_token=self.refresh_token)
                self.logged_in = True
                self.home()

    def settings(self, action="", param=""):
        if self.logged_in:
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(self.displaybox)
            self.label = Gtk.Label()
            self.label.set_css_classes(["text"])
            self.displaybox.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Settings</span>')

            # country setting

            countrylabel = Gtk.Label()
            countrylabel.set_markup('<span size="medium">  \nCountry</span>')
            self.displaybox.append(countrylabel)
            
            self.countrydd = Gtk.DropDown()
            self.countrydd.set_css_classes(["settings"])
            #self.countrydd.connect("notify::selected-item", self.set_country)
            self.displaybox.append(self.countrydd)

            strings = Gtk.StringList()
            self.countrydd.props.model = strings
            countries = requests.get("https://appgateway.lidlplus.com/configurationapp/v3/countries").json()
            items = ""
            for country in countries:
                items = items+" "+country["id"]
            items = items.split()

            for item in items:
                strings.append(item)

            self.countrydd.set_selected(items.index(self.country))

            # store selector

            storelabel = Gtk.Label()
            storelabel.set_markup('<span size="medium">  \n  \nStore</span>')
            
            self.displaybox.append(storelabel)

            self.storedd = Gtk.DropDown()
            self.storedd.set_css_classes(["settings"])
            self.displaybox.append(self.storedd)

            strings = Gtk.StringList()
            self.storedd.props.model = strings
            stores = requests.get(f"https://stores.lidlplus.com/api/v4/{self.country}").json()
            items = ""
            for store in stores:
                items = items+store["name"]+": "+store["storeKey"]+"div"
            items = items.split("div")

            for item in items:
                strings.append(item)
                if item.endswith(self.store):
                    self.storedd.set_selected(items.index(item))

            # save button
            save = Gtk.Button(label="Save")
            save.set_css_classes(["login-boxes"])
            save.connect("clicked", self.save)
            self.displaybox.append(save)
    
    def save(self, action):
        #box = action.get_parent()
        #country = box.get_first_child().get_next_sibling().get_next_sibling()
        #store = country.get_next_sibling().get_next_sibling()
        
        #country_selection = country.get_selected_item().get_string()
        country_selection = self.countrydd.get_selected_item().get_string()
        #store_selection = store.get_selected_item().get_string()
        store_selection = self.storedd.get_selected_item().get_string()
        self.country = country_selection
        self.store = store_selection.split(": ")[1]
        with open("login.json", "w") as login:
            login.write(json.dumps({"refresh_token": self.lidl._refresh_token, "country": self.country, "store": self.store}))
        self.home()

    def set_country(self, dropdown, _pspec):
        self.country=dropdown.props.selected_item.props.string
        if self.country != None:
            pass

    def purchaseLottery(self, action):
        if self.logged_in:
            self.displaybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(self.displaybox)
            self.label = Gtk.Label()
            self.label.set_css_classes(["text"])
            self.displaybox.append(self.label)
            if len(self.lidl.home(self.store)["purchaseLottery"]) == 0:
                self.label.set_markup('<span size="larger" weight="bold">There are no scratch coupons to redeem</span>')
            else:
                self.label.set_markup('<span size="larger" weight="bold">Redeeming</span>')
                # here comes the fun
                coupon_id = self.lidl.home(self.store)["purchaseLottery"][0]["id"]
                details = self.lidl.purchaseLottery_details(coupon_id=coupon_id)
                if self.lidl.redeem_purchaseLottery(coupon_id=coupon_id):
                    try:
                        for i in range(0,5):
                            status = self.lidl.purchaseLottery_status(coupon_id=coupon_id)
                            if status.startswith("0") or status == "":
                                break
                            else:
                                time.sleep(0.5)
                        if status.startswith("0") or status == "":
                            pass
                        else:
                            raise Exception("redeem error")
                    except:
                        self.label.set_markup(f"<span size='larger' weight='bold'>Couldn't redeem</span>")
                        self.home()
                    self.label.set_markup('<span size="larger" weight="bold">Successfully redeemed!</span>')
                    time.sleep(1)
                    self.coupons()
                            
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="xyz.zsobix.lidlplusui")
app.run(sys.argv)
