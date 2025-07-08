# import local files
from finances.classes.spreadsheet_analyzer import SpreadsheetAnalyzer


def main() -> None:
    analyzer = SpreadsheetAnalyzer()

    # Analyze spreadsheet
    analyzer.analyze_spreadsheet()
    analyzer.write_files()

    print("Analyzed Google Sheets spreadsheet")


if __name__ == "__main__":
    main()
