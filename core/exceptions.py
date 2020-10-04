class CustomValidationError(ValueError):

    def __init__(self, message, field):
        self.field = field
        self.message = message
