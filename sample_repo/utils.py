# sample_repo/utils.py
import datetime

def format_date(dt):
    """Formats a datetime object into a standard string."""
    if not isinstance(dt, datetime.datetime):
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Buggy function with potential AttributeError
def get_user_initials(user):
    """Extracts initials from a user object."""
    # This will raise an AttributeError if user.name is None or not a string
    names = user.name.split()
    return names[0][0] + names[-1][0]