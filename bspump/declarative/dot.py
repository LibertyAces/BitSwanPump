from .abc import Expression, SequenceExpression
from .expression.value.valueexpr import VALUE


def declaration_to_dot(decl, fname):
	with open(fname, "w") as fo:
		return declaration_to_dot_stream(decl, fo)


def declaration_to_dot_stream(decl, ostream):
	nodes = set()
	links = set()

	ostream.write("digraph G {\n\trankdir=LR;\n\tgraph [fontname = \"helvetica\"];\n\tnode [fontname = \"helvetica\"];\n\tedge [fontname = \"helvetica\"];\n")

	for parent, key, obj in decl.walk():

		if parent is not None:
			nodes.add(parent)

		if isinstance(obj, Expression):
			nodes.add(obj)

			if (parent is not None) and (parent.Id, obj.Id, key) not in links:
				if obj in nodes:
					style = "dashed"  # Link by alias
				else:
					style = "filled"

				ostream.write("\t\"{}\" -> \"{}\" [style={},label=\"{}\"];\n".format(parent.Id, obj.Id, style, key))
				links.add((parent.Id, obj.Id, key))

		else:
			vid = '.{}.val'.format(parent.Id)
			if (parent.Id, vid, key) not in links:
				ostream.write("\t\"{}\" -> \"{}\" [label=\"{}\"];\n".format(parent.Id, vid, key))
				ostream.write("\t\"{}\" [shape=box,label=\"<{}>\\n{}\"]\n".format(
					vid,
					obj.__class__.__name__,
					obj
				))
				links.add((parent.Id, vid, key))

	for obj in nodes:
		if isinstance(obj, SequenceExpression):
			shape = "hexagon"
			addinfo = ""
		elif isinstance(obj, VALUE):
			shape = "box"
			addinfo = "\\n" + str(obj.Value)
		else:
			shape = "octagon"
			addinfo = ""

		ostream.write("\t\"{}\" [label=\"<{}>\\n{}{}\",shape=\"{}\",style=filled,fillcolor=lightgray];\n".format(
			obj.Id,
			obj.Outlet,
			obj.__class__.__name__,
			addinfo,
			shape
		))

	ostream.write("}\n")
