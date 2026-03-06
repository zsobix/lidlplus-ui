import base64
import logging
import re
from datetime import datetime, timedelta, timezone
import string
import requests
import hashlib
from jwkest import b64e
from secrets import choice
from playwright.sync_api import sync_playwright
import random
class LidlPlusLogin:

    def __init__(self, language, country, refresh_token=""):
        self._login_url = ""
        self._code_verifier = ""
        self._code_challenge = ""
        self._refresh_token = refresh_token
        self._expires = None
        self._token = ""
        self._country = country.upper()
        self._language = language.lower()
        self._basech = string.ascii_letters + string.digits + "-._~"

    def add_code_challenge(self):
            cv_len = 64  # Use default

            code_verifier = "".join([choice(self._basech) for _ in range(cv_len)])
            _cv = code_verifier.encode("ascii")

            _method = "S256"

            try:
                _h = hashlib.sha256(_cv).digest()
                code_challenge = b64e(_h).decode("ascii")
            except KeyError:
                raise Unsupported("PKCE Transformation method:{}".format(_method)) from None

            # TODO store code_verifier

            return (
                {"code_challenge": code_challenge, "code_challenge_method": _method},
                code_verifier,
            )
    def _register_oauth_client(self):
        if self._login_url:
            return self._login_url
        self._code_challenge, self._code_verifier = self.add_code_challenge()
        self._login_url = f"https://accounts.lidl.com/connect/authorize/callback?client_id=LidlPlusNativeClient&response_type=code&scope=openid profile offline_access lpprofile lpapis&redirect_uri=com.lidlplus.app://callback&code_challenge={self._code_challenge["code_challenge"]}&code_challenge_method=S256"
        return self._login_url

    @property
    def _register_link(self):
        args = {
            "Country": self._country,
            "language": f"{self._language}-{self._country}",
        }
        params = "&".join([f"{key}={value}" for key, value in args.items()])
        return f"{self._register_oauth_client()}&{params}"
    
    @property
    def _login_form_link(self):
        self._form_link = f"https://accounts.lidl.com/Account/Login?ReturnUrl=/connect/authorize/callback?client_id=LidlPlusNativeClient&response_type=code&scope=openid profile offline_access lpprofile lpapis&redirect_uri=com.lidlplus.app://callback&code_challenge={self._code_challenge["code_challenge"]}&code_challenge_method=S256&Country={self._country}&language={self._language}-{self._country}"
        return self._form_link

    def _api_link(self, requested):
        url = f"https://appgateway.lidlplus.com/app/v23/{self._country}/{requested}"
        return url
        

    def login(self, email, password, **kwargs):
        """Simulate app auth"""
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            page = browser.new_page()
            response = page.goto(self._register_link)
            page.wait_for_timeout(random.randint(476, 975))
            #wait.until(expected_conditions.visibility_of_element_located((By.ID, "button_welcome_login"))).click()
            page.get_by_test_id("button-primary").click()
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("input-email").fill(email)
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("login-input-password").click()
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("login-input-password").fill(password)
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("button-primary").click()
            regx = re.search(r"https:\/\/accounts.lidl.com\/Account\/Login.*", response.request.redirected_from.redirected_to.url)
            if not regx:
                    raise Exception("LoginError")
            with page.expect_response("https://accounts.lidl.com/connect/authorize/**") as response:
                    authlink = response.value.all_headers()["location"]
                    authlink = authlink.replace("&", "?")
                    authlist = authlink.split("?")
                    authcode = authlist[1].replace("code=", "")
            browser.close()
            return f"Your refresh token is {authcode}"

email = input("Your email address: ")
password = input("Your password: ")
country = input("Your country code: ")
language = input("Your language code: ")
lidl = LidlPlusLogin(country=country, language=language)
print(lidl.login(email=email, password=password))