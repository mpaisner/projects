class PredFormat:
	
	def __init__(self, formatstr = None):
		self.formatstr = formatstr
	
	def format(self, statement):
		if self.formatstr:
			dict = {"pred": statement.predicate}
			dict.update({"arg" + str(i + 1): statement.args[i] for i in range(len(statement.args))})
			return self.formatstr % dict

DIVIDE_FORMAT = PredFormat("%(arg1)s %(pred)s %(arg2)s")