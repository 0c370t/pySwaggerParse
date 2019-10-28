from pySwaggerParse.helpers import swagger_py_type_lookup, get_type, parameter_as_type_gate


def build_list_model(model):
    if model["type"] != "array":
        raise Exception("This function requires an array!")
    if get_type(model["items"]) != "":
        contained_type = get_type(model["items"])
    else:
        contained_type = get_type(model) + "Items"
        if contained_type not in models:
            if "enum" in model["items"]:
                models[contained_type + "Items"] = build_enum_model(model["items"], get_type(model) + "Items")
            if "properties" in model["items"]:
                models[contained_type + "Items"] = build_object_model(model["items"], get_type(model) + "Items")
    if "description" in model:
        docstring = \
"""\"\"\"
        %s
    \"\"\"""" % ".\n       ".join(model["description"].split("."))
    else:
        docstring = ""
    return """

class %s(list):
    %s
    def __init__(self):
        super().__init__()
        self.T = %s

    def __setitem__(self, key, item):
        if type(item) is self.T:
            super().__setitem__(key, item)""" % (
        get_type(model),
        docstring,
        contained_type
    )


def build_object_model(model, forced_name=""):
    if model["type"] != "object":
        raise Exception("This function requires an object to model")
    # Build Required Parameters
    required_property_param = ", ".join(model["required"])
    required_property_set = []
    for r in model["required"]:
        required_property_set += ["self.%s = %s" % (r, r)]

    # Build Optional Parameters
    optional_params = []
    for param in model["properties"]:
        if param not in model["required"]:
            optional_params.append(param)
    optional_property_param = ", ".join(optional_params)
    optional_property_set = []
    for o in optional_params:
        optional_property_set += ["self.%s = %s" % (o, o)]

    all_property_set = []
    for param in model["properties"]:
        all_property_set.append(parameter_as_type_gate(model["properties"][param], 3, param))
    all_property_set += required_property_set + optional_property_set
    model_name = forced_name if forced_name != "" else get_type(model)
    if "description" in model:
        docstring = \
"""\"\"\"
        %s
    \"\"\"""" % ".\n       ".join(model["description"].split("."))
    else:
        docstring = ""
    return """

class %s:
    %s
    def __init__(self%s%s):
        %s""" % (
        model_name,
        docstring,
        ", " + required_property_param if len(required_property_param) > 0 else "",
        ", " + optional_property_param if len(optional_property_param) > 0 else "",
        "\n        ".join(all_property_set) if len(all_property_set) > 0 else "pass\n",
    )


def build_enum_model(e, force_name=""):
    enum_values = []
    for v in e["enum"]:
        enum_values += ["%s = '%s'" % (v.replace("#", "_").replace("-", "_"), v)]
    model_name = force_name if force_name != "" else get_type(e)
    if "description" in e:
        docstring = \
"""\"\"\"
        %s
    \"\"\"""" % ".\n       ".join(e["description"].split("."))
    else:
        docstring = ""
    return """

class %s(Enum):
    %s
    %s""" % (
        model_name,
        docstring,
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
                elif "$ref" not in parameter:
                    recursively_identify_models(parameter)
        if "get" in swagger_definition["paths"][pathName]:
            for parameter in swagger_definition["paths"][pathName]["get"]["parameters"]:
                if "schema" in parameter:
                    recursively_identify_models(parameter["schema"])
                elif "$ref" not in parameter:
                    recursively_identify_models(parameter)

    for parameter in swagger_definition["parameters"].values():
        recursively_identify_models(parameter)

    with open(root_path, "w") as f:
        f.write("from enum import Enum\n")
        for model_key in sorted(models.keys()):
            if model_key != "":
                f.write(models[model_key] + "\n")
