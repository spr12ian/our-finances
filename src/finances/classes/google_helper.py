import json
from collections.abc import Sequence
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from finances.classes.config import Config
from finances.classes.exception_helper import ExceptionHelper

class GoogleHelperError(ExceptionHelper):
    pass

class GoogleHelper:
    def __init__(self) -> None:
        self.read_config()
        self.check_config_values()


    def check_config_values(self) -> None:
        service_account_key_file = Path(self.service_account_key_file)
        if not service_account_key_file.exists():
            raise GoogleHelperError(
                f"Credentials file '{service_account_key_file}' does not exist."
            ) from FileNotFoundError(service_account_key_file)

        try:
            with open(service_account_key_file, encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"{service_account_key_file}: Invalid JSON: {e}"
            ) from e
        except OSError as e:
            raise OSError(
                f"Error reading service account file '{service_account_key_file}': {e}"
            ) from e
        
        spreadsheet_key=self.spreadsheet_key
        if not spreadsheet_key:
            raise GoogleHelperError(
                f"Missing spreadsheet key '{spreadsheet_key}'"
            ) from OSError(spreadsheet_key)


    def get_authorized_client(self, scopes: Sequence[str]) -> gspread.Client:
        # from_service_account_file requires scopes to be passed as a keyword arguement

        # creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        credentials = self.get_credentials(scopes)

        client = gspread.authorize(credentials)

        return client

    def get_credentials(self, scopes: Sequence[str]) -> Credentials:
        service_account_file: str = self.service_account_key_file
        credentials: Credentials = Credentials.from_service_account_file(  # type: ignore
            service_account_file, scopes=scopes
        )
        return credentials

    def get_spreadsheet(self, scopes: list[str]) -> gspread.Spreadsheet:
        client: gspread.Client = self.get_authorized_client(scopes)
        spreadsheet: gspread.Spreadsheet = client.open_by_key(self.spreadsheet_key)

        return spreadsheet

    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    def read_config(self) -> None:
        config = Config()

        # Google Cloud Service credentials
        service_account_key_file = config.GOOGLE_SERVICE_ACCOUNT_KEY_FILE
        self.service_account_key_file = service_account_key_file

        spreadsheet_key = config.OUR_FINANCES_DRIVE_KEY
        self.spreadsheet_key = spreadsheet_key
