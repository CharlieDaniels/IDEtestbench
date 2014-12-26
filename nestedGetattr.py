def nestedGetattr(object, attr_one, attr_two):
  nested_object = getattr(object, attr_one)
  return getattr(nested_object, attr_two)