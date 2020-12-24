from datetime import datetime
from dateutil import parser
import pytz

def get_validity_time():
    """
    This method wraps datetime.now() because it must be possible to override it during tests.
    :return: current datetime.
    """
    return datetime.now().replace(microsecond=0)

def get_utc_datetime_from_iso8601_string(iso_8601_string):

    dt=  parser.parse(iso_8601_string).astimezone(pytz.utc)
    return dt.replace(tzinfo=None)
