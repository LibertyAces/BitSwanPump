from .abc import Expression, SequenceExpression


def declaration_to_dot(decl, fname):
	nodes = set()
	links = set()

	with open(fname, "w") as fo:
		fo.write("digraph G {\n\trankdir=LR;\n")

		for parent, key, obj in decl.walk():

			if parent is None:
				continue
			nodes.add(parent)

			if isinstance(obj, Expression):
				if (parent.Id, obj.Id, key) not in links:
					if obj in nodes:
						style = "dashed"  # Link by alias
					else:
						style = "filled"

					fo.write("\t\"{}\" -> \"{}\" [style={},label=\"{}\"];\n".format(parent.Id, obj.Id, style, key))
					nodes.add(obj)
					links.add((parent.Id, obj.Id, key))

			else:
				vid = '.{}.val'.format(parent.Id)
				if (parent.Id, vid, key) not in links:
					fo.write("\t\"{}\" -> \"{}\" [label=\"{}\"];\n".format(parent.Id, vid, key))
					fo.write("\t\"{}\" [shape=box,label=\"<{}>\\n{}\"]\n".format(
						vid,
						obj.__class__.__name__,
						obj
					))
					links.add((parent.Id, vid, key))

		for obj in nodes:
			if isinstance(obj, SequenceExpression):
				shape = "doubleoctagon"
			else:
				shape = "octagon"

			fo.write("\t\"{}\" [label=\"<{}>\\n{}\",shape=\"{}\"];\n".format(
				obj.Id,
				obj.get_outlet_type(),
				obj.__class__.__name__,
				shape
			))

		fo.write("}\n")
