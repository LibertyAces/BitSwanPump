import itertools

from .abc import Expression, SequenceExpression


def declaration_to_dot(decl, fname):
	nodes = set()
	vidgen = itertools.count(1)

	with open(fname, "w") as fo:
		fo.write("digraph G {\n\trankdir=LR;\n")

		for parent, key, obj in decl.walk():

			if parent is None:
				continue

			if isinstance(obj, Expression):
				fo.write("\t{} -> {} [label=\"{}\"];\n".format(parent.Id, obj.Id, key))
				nodes.add(obj)
				nodes.add(parent)
			else:
				vid = 'V{}'.format(next(vidgen))
				fo.write("\t{} -> {} [label=\"{}\"];\n".format(parent.Id, vid, key))
				fo.write("\t{} [shape=box,label=\"<{}>\\n{}\"]\n".format(
					vid,
					obj.__class__.__name__,
					obj
				))

		for obj in nodes:
			if isinstance(obj, SequenceExpression):
				shape = "doubleoctagon"
			else:
				shape = "octagon"

			fo.write("\t{} [label=\"<{}>\\n{}\",shape=\"{}\"];\n".format(
				obj.Id,
				obj.get_type(),
				obj.__class__.__name__,
				shape
			))

		fo.write("}\n")
