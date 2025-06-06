from collections.abc import Sequence

import gspread
from google.oauth2.service_account import Credentials

from finances.classes.config import Config
from finances.classes.os_helper import OsHelper


class GoogleHelper:
    def __init__(self) -> None:
        self.read_config()

    def get_authorized_client(self, scopes: Sequence[str]) -> gspread.Client:
        # from_service_account_file requires scopes to be passed as a keyword arguement

        # creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        credentials = self.get_credentials(scopes)

        client = gspread.authorize(credentials)

        return client

    def get_credentials(self, scopes: Sequence[str]) -> Credentials:
        service_account_file: str = self.get_credentials_path()
        credentials: Credentials = Credentials.from_service_account_file(  # type: ignore
            service_account_file, scopes=scopes
        )
        return credentials

    def get_credentials_path(self) -> str:
        credentials_path = f"{self.service_account_key_file}"

        return credentials_path

    def get_spreadsheet(self, scopes: list[str]) -> gspread.Spreadsheet:
        client: gspread.Client = self.get_authorized_client(scopes)
        spreadsheet: gspread.Spreadsheet = client.open_by_key(self.spreadsheet_key)

        return spreadsheet

    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    def read_config(self) -> None:
        config = Config()

        # Google Cloud Service credentials
        service_account_key_file = config.get("GOOGLE_SERVICE_ACCOUNT_KEY_FILE")
        if not service_account_key_file:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_KEY_FILE is not set in the configuration."
            )
        if not service_account_key_file.endswith(".json"):
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY_FILE must be a JSON file.")
        if not OsHelper().file_exists(service_account_key_file):
            raise FileNotFoundError(
                f"Credentials file '{service_account_key_file}' does not exist."
            )
        spreadsheet_key = config.get("GOOGLE_DRIVE_OUR_FINANCES_KEY")
        if not spreadsheet_key:
            raise ValueError(
                "GOOGLE_DRIVE_OUR_FINANCES_KEY is not set in the configuration."
            )

        self.service_account_key_file = service_account_key_file
        self.spreadsheet_key = spreadsheet_key
