

def type_inference(app, expression):
	print("INFERENCE!")

	for parent, key, obj in expression.walk():
		print(">", parent, key, obj, obj.Outlet.Type.Name)

	print("----")
	return expression
