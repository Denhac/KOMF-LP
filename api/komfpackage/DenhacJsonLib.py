import datetime, json
from flask import jsonify

class JsonTools:

	def __init__(self):
		pass

	def JsonDefaultMappings(value):
		if isinstance(value, datetime.date):
			return dict(year=value.year, month=value.month, day=value.day)
		# TODO - handle datetime and other non-default-included objects here if necessary
		else:
			return value.__dict__

	def ObjToJson(obj):
		return json.dumps(obj, default=JsonTools.JsonDefaultMappings)

	def JsonToObj(jsonStr):
		return json.loads(jsonStr)

	def Reply(replydict):
		return jsonify(replydict)

	# Python 2.x way of declaring static functions
	JsonDefaultMappings = staticmethod(JsonDefaultMappings)
	ObjToJson           = staticmethod(ObjToJson)
	JsonToObj           = staticmethod(JsonToObj)
	Reply               = staticmethod(Reply)
