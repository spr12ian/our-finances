from datetime import datetime


class DateTimeHelper:
    ISO_DATE_FORMAT = "%Y-%m-%d"
    UK_DATE_FORMAT = "%d/%m/%Y"

    # Function to convert UK date strings (DD/MM/YYYY) to ISO date strings YYYY-MM-DD
    def ISO_to_UK(self, date_str:str) -> str:
        return self.reformat_date_str(
            date_str, DateTimeHelper.ISO_DATE_FORMAT, DateTimeHelper.UK_DATE_FORMAT
        )

    # Function to convert UK date strings (DD/MM/YYYY) to ISO date strings YYYY-MM-DD
    def UK_to_ISO(self, date_str: str) -> str:
        return self.reformat_date_str(
            date_str, DateTimeHelper.UK_DATE_FORMAT, DateTimeHelper.ISO_DATE_FORMAT
        )

    # Function to format date with ordinal day
    def format_date_with_ordinal(self, date: datetime) -> str:
        day = date.day
        suffix = self.get_ordinal_suffix(day)
        return date.strftime(f"%A, %B {day}{suffix}, %Y")

    def get_date_today(self)->str:
        now = datetime.now()
        return self.format_date_with_ordinal(now)

    # Function to determine the ordinal suffix
    def get_ordinal_suffix(self, day: int) -> str:
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return suffix

    def get_time_now(self) -> str:
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def reformat_date_str(self, date_str: str, from_format: str, to_format: str) -> str:
        if date_str.strip() == "":  # Check if the string is empty or whitespace
            return ""

        # Convert the string to a datetime object
        date_obj = datetime.strptime(date_str, from_format)

        # Convert the datetime object back to a string in the desired format
        return date_obj.strftime(to_format)
