class ForexException(Exception):
    def __init__(self, exception):
        self.exception = exception

    def get_exception(self):
        return self.exception

    def get_error_message(self):
        return self.exception.get('ErrorMessage')

    def get_status_code(self):
        return self.exception('StatusCode')

    def get_additional_info(self):
        return self.exception.get('AdditionalInfo')

    def get_http_status(self):
        return self.exception.get('HttpStatus')

    def get_error_code(self):
        return self.exception.get('ErrorCode')
