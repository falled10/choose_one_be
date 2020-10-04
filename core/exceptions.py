class CustomValidationError(ValueError):
    """Use this validation for when you make validation
    and want to set message to exact field
    """

    def __init__(self, message, field):
        self.field = field
        self.message = message
