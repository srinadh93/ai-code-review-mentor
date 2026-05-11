# sample_repo/tests/test_user.py
import pytest
from models import User

# This test will fail because User.__init__ doesn't exist and the default
# constructor will happily accept a User without an email, but other parts
# of an application might assume email is always present.
def test_user_creation_no_email():
    with pytest.raises(TypeError):
        # This should raise an error, but it won't with the current model.
        # A well-defined __init__ would enforce this.
        _ = User(name="Test User") 

def test_user_validation():
    user = User(name="Valid User", email="test@example.com")
    assert user.validate_email() is True

    user_bad_email = User(name="Invalid User", email="bad-email")
    with pytest.raises(ValueError):
        user_bad_email.validate_email()