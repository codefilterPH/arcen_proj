from datetime import datetime
from django.utils import timezone
import pytz

class DateTimeConverter:
    @staticmethod
    def get_current_time():
        try:
            current_time = datetime.now(pytz.utc)
            return current_time.astimezone(pytz.timezone('Asia/Manila'))
        except Exception as ex:  # Corrected 'exception' to 'except'
            # logging.error(f'AN ERROR OCCURRED GETTING CURRENT TIME FUNCTION: {str(ex)}')
            print(f'RETURNING TIMEZONE.NOW() TIME')
            return timezone.now()

    @staticmethod
    def military_format(datetime_str):
        # Check if the datetime_str is None or the string 'None'
        if not datetime_str or datetime_str == 'None':
            return 'N/A'  # You can return a default value or handle it accordingly

        try:
            # Parse the input string to a datetime object, including timezone information
            datetime_obj = datetime.fromisoformat(str(datetime_str))

            # Convert to the desired format
            return datetime_obj.strftime('%d %B %Y, %H:%M')  # Example: 22 August 2025, 10:20
        except ValueError:
            return 'Invalid Date'  # Or handle invalid datetime formats as needed

    @staticmethod
    def military_dateformat(datetime_str):
        # Check if the datetime_str is None or the string 'None'
        if not datetime_str or datetime_str == 'None':
            return 'N/A'  # You can return a default value or handle it accordingly

        try:
            # Parse the input string to a datetime object, including timezone information
            datetime_obj = datetime.fromisoformat(str(datetime_str))

            # Convert to the desired format (date only)
            return datetime_obj.strftime('%d %B %Y')  # Example: 22 August 2025
        except ValueError:
            return 'Invalid Date'  # Or handle invalid datetime formats as needed

    @staticmethod
    def convert_to_dd_mm_yyyy_hh_mm(datetime_str):
        """
        Converts a datetime string in ISO 8601 format ('YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM')
        to 'DD-MM-YYYY HH:MM'.

        :param datetime_str: Input datetime string.
        :return: Formatted date as a string in 'DD-MM-YYYY HH:MM'.
        :raises ValueError: If the input format is invalid.
        """
        try:
            # Parse the ISO 8601 datetime string
            dt = datetime.fromisoformat(str(datetime_str))

            # Convert to the desired format
            formatted_date = dt.strftime('%d-%m-%Y %H:%M')
            return formatted_date
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {datetime_str}. "
                             "Expected format: 'YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM'.") from e
