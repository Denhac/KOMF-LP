class DenhacException(Exception):
	status_code = 0

	def __init__(self, error, status_code, payload=None):
		Exception.__init__(self)
		self.error   = error
		status_code  = status_code
		self.payload = payload

	def to_dict(self):
		retval = dict(self.payload or ())
		retval['error'] = self.error
		return retval

class BadRequestException(DenhacException):
	def __init__(self, error, payload=None):
		DenhacException.__init__(self, error=error, status_code=400, payload=payload)

class NotFoundException(DenhacException):
	def __init__(self):
		DenhacException.__init__(self, error="File or Directory Not Found", status_code=404, payload=None)

class MethodNotAllowedException(DenhacException):
	def __init__(self):
		DenhacException.__init__(self, error="The method is not allowed for the requested URL.", status_code=405, payload=None)

class InternalServerErrorException(DenhacException):
	def __init__(self, error, payload=None):
		DenhacException.__init__(self, error=error, status_code=500, payload=payload)
		if self.payload is None:
			self.payload = dict()
		self.payload['message'] = "Internal Server Error"
