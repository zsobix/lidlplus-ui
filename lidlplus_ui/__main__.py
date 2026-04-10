from .ui import MyApp
import argparse
from lidlplus_api import LidlPlusApi
    
def get_arguments():
    """Get parsed arguments."""
    parser = argparse.ArgumentParser(
        prog="lidlplus-ui",
        description="Lidl Plus on Desktop",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=28),
    )
    parser.add_argument("auth", help="authenticate and print refresh_token")
    return vars(parser.parse_args())

def lidl_plus_login():
    language = input("Enter your language (de, en, ...): ")
    country = input("Enter your country (DE, AT, ...): ")
    username = input("Enter your lidl plus username (phone number): ")
    password = input("Enter your lidl plus password: ")
    api = LidlPlusApi(language, country)
    api.login(email=username,password=password)
    print(f"Your refresh token is: {api._refresh_token}")


def main():
    args = get_arguments()
    if args.get("auth"):
        lidl_plus_login()
    else:
        app = MyApp(application_id="xyz.zsobix.lidlplusui")
        app.run()

if __name__ == "__main__":
    main()