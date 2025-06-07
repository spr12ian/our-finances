from finances.classes.config import Config

config = Config()

# Accessing values

print("Spreadsheet Key:", config.get("Google.Sheets.spreadsheet_key"))
print("Convert Tables:", config.get("Google.Sheets.convert_account_tables"))
print("SQLite DB:", config.get("SQLite.database_name"))
print("Spreadsheet Key:", config.Google.Sheets.spreadsheet_key)
print("Convert Tables:", config.Google.Sheets.convert_account_tables)
print("SQLite DB:", config.SQLite.database_name)
