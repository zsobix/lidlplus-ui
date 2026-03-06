import sys
import gi
sys.path.append('./lidlplus-api/')
import api
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

css_provider = Gtk.CssProvider()
css_provider.load_from_path('style.css')
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here
        self.logged_in = False
        self.store = ""

        self.set_default_size(600, 250)
        self.set_title("Lidl Plus on Desktop")
        self.titlebar = Gtk.HeaderBar()
        self.set_titlebar(self.titlebar)
        
        self.home()

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

        self.purchaseLotterybutton = Gtk.Button()
        self.purchaseLotterybutton.connect("clicked", self.purchaseLottery)
        #self.purchaseLotterybutton.set_icon_name("package-x-generic-symbolic")
        self.purchaseLotterybutton.set_icon_name("auth-smartcard-symbolic")
        self.titlebar.pack_start(self.purchaseLotterybutton)

    def logout(self, action="", param=""):
        os.remove("login.json")
        self.logged_in = False
        self.home()
    def coupons(self, action="", param=""):
        if self.logged_in:
            scrollwin = Gtk.ScrolledWindow.new()
            self.set_child(scrollwin)
            self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.box1)
            self.label = Gtk.Label()
            self.box1.append(self.label)
            activecoupons = self.lidl.activecoupons_count(self.store)["activeCount"]
            self.label.set_markup(f'<span size="larger" weight="bold">Coupons\nActive coupons count: {activecoupons}</span>')
            self.label.set_css_classes(["text"])
            coupons = self.lidl.coupons(self.store)["sections"][0]["promotions"]
            for coupon in coupons:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.box1.append(activate)
                activate.connect("clicked", self.details)
                centerbox = Gtk.CenterBox()
                activate.set_child(centerbox)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.box1.append(box)
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
        print(text.split("div"))
        info = text.split("div")
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box1)

        home_button = Gtk.Button(label="Back")
        home_button.connect("clicked", self.coupons)
        home_button.set_css_classes(["button"])
        self.box1.append(home_button)

        image = Gtk.Picture().new_for_filename(f"{info[0]}.jpg")
        image.set_css_classes(["picture"])
        self.box1.append(image)

        title = Gtk.Label()
        title.set_markup(f'<span size="200%">{info[3]}\n{info[2]} day(s) left</span>')
        title.set_css_classes(["description"])
        self.box1.append(title)

        button = Gtk.Button(label="test")
        button.set_css_classes(['button'])
        button.connect("clicked", self.toggle)
        self.box1.append(button)

        buttontext = Gtk.Label()
        button.set_child(buttontext)
        if info[1] == "False":
            buttontext.set_markup(f'<span size="1%">{info[0]}div{info[1]}div</span><span size="200%">Activate</span>')
        else:
            buttontext.set_markup(f'<span size="1%">{info[0]}div{info[1]}div</span><span size="200%">Deactivate</span>')

    def toggle(self, action):
        label = action.get_child()
        info = label.get_text().split("div")
        print(info)
        isActivated = info[1]
        coupon_id = info[0]
        if isActivated == "True":
            if self.lidl.deactivate_coupon(coupon_id=coupon_id):
                print("success")
                self.coupons()
            else:
                print("not successful")
        else:
            if self.lidl.activate_coupon(coupon_id=coupon_id):
                print("success")
                self.coupons()
            else:
                print("not successful")


    def offers(self, action="", param=""):
         if self.logged_in:
            scrollwin = Gtk.ScrolledWindow.new()
            self.set_child(scrollwin)
            self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.box1)
            self.label = Gtk.Label()
            self.box1.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Offers</span>')
            self.label.set_css_classes(["text"])
            print(self.lidl.offers(self.store))
            offers = self.lidl.offers("HU0358")["offers"]
            for offer in offers:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.box1.append(activate)
                #activate.connect("clicked", self.details)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.box1.append(box)
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
            self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            scrollwin.set_child(self.box1)
            self.label = Gtk.Label()
            self.box1.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Coupons</span>')
            self.label.set_css_classes(["text"])
            brochures = self.lidl.brochures(self.store)[0]["flyers"]
            for brochure in brochures:
                activate = Gtk.Button() #label="Activate/Deactivate"
                activate.set_css_classes(['button'])
                self.box1.append(activate)
                activate.connect("clicked", self.brochuredetails)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                #self.box1.append(box)
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
        print(text.split("div"))
        info = text.split("div")
        webbrowser.open(info[0])

    def login(self, action):
        if not os.path.exists("login.json"):
            self.lidl = api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper())
            self.lidl.login(email=self.usernameentry.get_text(), password=self.passwordentry.get_text())
            self.store = requests.get(f"https://stores.lidlplus.com/api/v4/{self.country}").json()[0]["storeKey"]
            with open("login.json", "w") as login:
                login.write(json.dumps({"refresh_token": self.lidl._refresh_token, "country": self.country, "store": self.store}))
        else:
            with open("login.json", "r") as login:
                jason = json.loads(login.read())
                refresh_token = jason["refresh_token"]
            self.lidl = api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper(), refresh_token=refresh_token)
        #print(self.usernameentry.get_text())
        #print(self.passwordentry.get_text())
        self.logged_in = True
        #print(self.lidl.offers("HU0358"))
        self.home()
    def home(self, action="", param=""):
        self.centerbox = Gtk.CenterBox()
        self.set_child(self.centerbox)
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.centerbox.set_center_widget(self.box1)
        self.box1.set_css_classes(["home"])
        self.label = Gtk.Label()
        self.label.set_css_classes(["text"])
        self.box1.append(self.label)
        if self.logged_in:
            if len(self.lidl.home(self.store)["purchaseLottery"]) == 0:
                self.label.set_markup('<span size="larger" weight="bold">Home</span>')
            else:
                self.label.set_markup(f'<span size="larger" weight="bold">Home\nYou have a scratch card to redeem!</span>')
            
            schedulebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.box1.append(schedulebox)
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
            self.box1.append(grid)

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

            couponbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            buttonsbox.append(couponbox)

            couponbutton = Gtk.Button(label="coupons")
            couponbutton.set_css_classes(['button'])
            couponbutton.connect("clicked", self.coupons)
            couponbox.append(couponbutton)

            couponlabel = Gtk.Label()
            couponlabel.set_markup('<span size="x-large">                         Coupons                         </span>')
            couponbutton.set_child(couponlabel)

            offerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            buttonsbox.append(offerbox)

            offerbutton = Gtk.Button(label="offers")
            offerbutton.set_css_classes(['button'])
            offerbutton.connect("clicked", self.offers)
            offerbox.append(offerbutton)

            offerlabel = Gtk.Label()
            offerlabel.set_markup('<span size="x-large">                          Offers                          </span>')
            offerbutton.set_child(offerlabel)

            brochuresbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            buttonsbox.append(brochuresbox)
            
            brochuresbutton = Gtk.Button(label="brochures")
            brochuresbutton.set_css_classes(['button'])
            brochuresbutton.connect("clicked", self.brochures)
            brochuresbox.append(brochuresbutton)

            brochureslabel = Gtk.Label()
            brochureslabel.set_markup('<span size="x-large">                           Brochures                            </span>')
            brochuresbutton.set_child(brochureslabel)

            settingsbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            buttonsbox.append(settingsbox)

            settingsbutton = Gtk.Button(label="settings")
            settingsbutton.set_css_classes(['button'])
            settingsbutton.connect("clicked", self.settings)
            settingsbox.append(settingsbutton)

            settingslabel = Gtk.Label()
            settingslabel.set_markup('<span size="x-large">                           Settings                            </span>')
            settingsbutton.set_child(settingslabel)
            

            logoutbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            buttonsbox.append(logoutbox)

            logoutbutton = Gtk.Button(label="logout")
            logoutbutton.set_css_classes(['button'])
            logoutbutton.connect("clicked", self.settings)
            logoutbox.append(logoutbutton)

            logoutlabel = Gtk.Label()
            logoutlabel.set_markup('<span size="x-large">                           Logout                            </span>')
            logoutbutton.set_child(logoutlabel)


            # store schedule

            #schedulebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            #self.box1.append(schedulebox)
            #schedule = Gtk.Label()
            #schedulebox.append(schedule)
            #store_schedule = self.lidl.store_schedule(self.store)
            #if store_schedule['isOpen'] == "False":
            #    schedule.set_markup(f'<span size="x-large">{self.lidl.store_details(self.store)[0]["name"]} (currently closed),\n\nopen from: {store_schedule["openingHours"][0]["from"]}\n\nto: {store_schedule["openingHours"][0]["to"]}</span>')
            #else:
            #    schedule.set_markup(f'<span size="x-large">{self.lidl.store_details(self.store)[0]["name"]} (currently open),\n\nopen from: {store_schedule["openingHours"][0]["from"]}\n\nto: {store_schedule["openingHours"][0]["to"]}</span>')
        if not self.logged_in:
            if not os.path.exists("login.json"):
                self.passwordbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.box1.append(self.passwordbox)
                self.passwordbox.set_css_classes(["login-boxes"])

                self.usernamebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.passwordbox.append(self.usernamebox)
                self.usernamebox.set_css_classes(["login-boxes"])

                self.usernameentry = Gtk.Entry()
                self.usernamebox.append(self.usernameentry)

                self.usernamelabel = Gtk.Label()
                self.usernamelabel.set_markup('<span size="medium">Email</span>')
                self.usernamebox.append(self.usernamelabel)

                self.passwordentry = Gtk.PasswordEntry()
                self.passwordbox.append(self.passwordentry)
                self.passwordentry.set_show_peek_icon(True)

                self.passwordlabel = Gtk.Label()
                self.passwordlabel.set_markup('<span size="medium">Password</span>')
                self.passwordbox.append(self.passwordlabel)

                self.countrybox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.passwordbox.append(self.countrybox)
                self.countrybox.set_css_classes(["login-boxes"])

                self.countrydd = Gtk.DropDown()
                self.countrydd.connect("notify::selected-item", self.set_country)
                self.countrybox.append(self.countrydd)

                strings = Gtk.StringList()
                self.countrydd.props.model = strings
                countries = requests.get("https://appgateway.lidlplus.com/configurationapp/v3/countries").json()
                items = ""
                for country in countries:
                    items = items+" "+country["id"]
                items = items.split()

                for item in items:
                    strings.append(item)

                self.countrylabel = Gtk.Label()
                self.countrylabel.set_markup('<span size="medium">Country</span>')
                self.countrybox.append(self.countrylabel)

                self.buttonbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.countrybox.append(self.buttonbox)
                self.buttonbox.set_css_classes(["login-boxes"])

                self.button = Gtk.Button(label="Login")
                self.buttonbox.append(self.button)
                self.button.connect("clicked", self.login)

                login_button_label = Gtk.Label()
                login_button_label.set_markup('<span size="large">Login</span>')
                self.button.set_child(login_button_label)
            else:
                with open("login.json", "r") as login:
                    jason = json.loads(login.read())
                    self.refresh_token = jason["refresh_token"]
                    self.country = jason["country"]
                    self.store = jason["store"]
                self.lidl = api.LidlPlusApi(language=str(self.country).lower(), country=str(self.country).upper(), refresh_token=self.refresh_token)
                self.logged_in = True
                self.home()

    def settings(self, action="", param=""):
        if self.logged_in:
            self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(self.box1)
            self.label = Gtk.Label()
            self.label.set_css_classes(["text"])
            self.box1.append(self.label)
            self.label.set_markup('<span size="larger" weight="bold">Settings</span>')

            # country setting

            self.countrylabel = Gtk.Label()
            self.countrylabel.set_markup('<span size="medium">  \nCountry</span>')
            self.box1.append(self.countrylabel)
            
            self.countrydd = Gtk.DropDown()
            self.countrydd.set_css_classes(["settings"])
            #self.countrydd.connect("notify::selected-item", self.set_country)
            self.box1.append(self.countrydd)

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

            self.storelabel = Gtk.Label()
            self.storelabel.set_markup('<span size="medium">  \n  \nStore</span>')
            
            self.box1.append(self.storelabel)

            self.storedd = Gtk.DropDown()
            self.storedd.set_css_classes(["settings"])
            #self.storedd.connect("notify::selected-item", self.set_country)
            self.box1.append(self.storedd)

            strings = Gtk.StringList()
            self.storedd.props.model = strings
            stores = requests.get(f"https://stores.lidlplus.com/api/v4/{self.country}").json()
            items = ""
            for store in stores:
                items = items+store["name"]+": "+store["storeKey"]+"div"
            items = items.split("div")

            for item in items:
                strings.append(item)

            for item in items:
                if item.endswith(self.store):
                    self.storedd.set_selected(items.index(item))

            # save button
            save = Gtk.Button(label="Save")
            save.set_css_classes(["login-boxes"])
            save.connect("clicked", self.save)
            self.box1.append(save)
    
    def save(self, action):
        #box = action.get_parent()
        #country = box.get_first_child().get_next_sibling().get_next_sibling()
        #store = country.get_next_sibling().get_next_sibling()
        
        #country_selection = country.get_selected_item().get_string()
        country_selection = self.countrydd.get_selected_item().get_string()
        print(country_selection)
        #store_selection = store.get_selected_item().get_string()
        store_selection = self.storedd.get_selected_item().get_string()
        print(store_selection.split(": ")[1])
        self.country = country_selection
        self.store = store_selection.split(": ")[1]
        with open("login.json", "w") as login:
            login.write(json.dumps({"refresh_token": self.lidl._refresh_token, "country": self.country, "store": self.store}))

    def set_country(self, dropdown, _pspec):
        self.country=dropdown.props.selected_item.props.string
        if self.country != None:
            print(f"Selected: {self.country}")

    def purchaseLottery(self, action):
        if self.logged_in:
            self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(self.box1)
            self.label = Gtk.Label()
            self.label.set_css_classes(["text"])
            self.box1.append(self.label)
            if len(self.lidl.home(self.store)["purchaseLottery"]) == 0:
                self.label.set_markup('<span size="larger" weight="bold">There are no scratch coupons to redeem</span>')
            else:
                self.label.set_markup('<span size="larger" weight="bold">Redeeming</span>')
                self.spinner = Gtk.Spinner()
                self.box1.append(self.spinner)
                self.spinner.start()
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
                        self.spinner.stop()
                        time.sleep(1)
                        self.home()
                    self.label.set_markup('<span size="larger" weight="bold">Successfully redeemed!</span>')
                    self.spinner.stop()
                    time.sleep(1)
                    self.coupons()
                            
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="xyz.zsobix.lidlplus")
app.run(sys.argv)
