from pySwaggerParse.helpers import swagger_py_type_lookup, get_type


def build_list_model(model):
    if model["type"] != "array":
        raise Exception("This function requires an array!")
    return """class %s(list):
    def __init__(self):
        super().__init__()
        self.T = %s

    def __setitem__(self, key, item):
        if type(item) is self.T:
            super().__setitem__(key, item)


""" % (
        get_type(model),
        get_type(model["items"])
    )


def build_object_model(model):
    if model["type"] != "object":
        raise Exception("This function requires an object to model")
    # Build Required Parameters
    required_property_param = ", ".join(model["required"])
    required_property_set = []
    for r in model["required"]:
        required_property_set += ["""if type(%s) is not %s:
            raise Exception("%s must be of type %s!")""" % (
            r,
            get_type(model["properties"][r]),
            r,
            get_type(model["properties"][r])
        )]
        required_property_set += ["self.%s = %s\n" % (r, r)]

    # Build Optional Parameters
    optional_params = []
    for param in model["properties"]:
        if param not in model["required"]:
            optional_params.append(param)
    optional_property_param = ", ".join(optional_params)
    optional_property_set = []
    for o in optional_params:
        optional_property_set += ["""if type(%s) is not %s:
            raise Exception("%s must be of type %s!")""" % (
            o,
            get_type(model["properties"][o]),
            o,
            get_type(model["properties"][o])
        )]
        optional_property_set += ["self.%s = %s\n" % (o, o)]

    all_property_set = required_property_set + optional_property_set
    return """class %s:
    def __init__(self%s%s):
        %s

""" % (
        get_type(model),
        ", " + required_property_param if len(required_property_param) > 0 else "",
        ", " + optional_property_param if len(optional_property_param) > 0 else "",
        "\n        ".join(all_property_set) if len(all_property_set) > 0 else "pass\n",
    )


def build_enum_model(e):
    enum_values = []
    for v in e["enum"]:
        enum_values += ["%s = '%s'" % (v.lstrip("#").replace("-","_"), v)]
    return """class %s(Enum):
    %s

    """ % (
        get_type(e),
        "\n    ".join(enum_values)
    )


models = {}


def recursively_identify_models(model_obj):
    if "properties" in model_obj:
        props = model_obj["properties"]
        for prop in props:
            if "type" in props[prop] and props[prop]["type"] not in swagger_py_type_lookup:
                recursively_identify_models(props[prop])
            elif "enum" in props[prop]:
                recursively_identify_models(props[prop])
        models[get_type(model_obj)] = build_object_model(model_obj)
    if "items" in model_obj:
        if "type" in model_obj["items"] and model_obj["items"]["type"] not in swagger_py_type_lookup:
            recursively_identify_models(model_obj["items"])

        models[get_type(model_obj)] = build_list_model(model_obj)

    if "enum" in model_obj:
        models[get_type(model_obj)] = build_enum_model(model_obj)


def create(swagger_definition, root_path):
    root_path.touch(exist_ok=True)
    for pathName in swagger_definition["paths"]:
        if "post" in swagger_definition["paths"][pathName]:
            for parameter in swagger_definition["paths"][pathName]["post"]["parameters"]:
                if "schema" in parameter:
                    recursively_identify_models(parameter["schema"])
    for parameter in swagger_definition["parameters"].values():
        recursively_identify_models(parameter)

    with open(root_path, "w") as f:
        f.write("from enum import Enum\n\n")
        for model in models.values():
            f.write(model+"\n")
