import email_validator
import validator


class EmailValidator(validator.Validator):

    err_message = 'must be a valid e-mail address'

    def __call__(self, value):
        try:
            email_validator.validate_email(value, check_deliverability=False)
        except email_validator.EmailNotValidError:
            return False
        else:
            return True
