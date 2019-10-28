from pySwaggerParse.config import forbidden_params, swagger_py_type_lookup


def get_http_method(path_obj):
    keys = list(path_obj.keys())
    keys.remove("path")
    return keys[0]


def trim_params(params, master_params):
    output = []
    for _param in params:
        if "$ref" in _param.keys():
            param_ref = _param["$ref"].replace("#/parameters/", "")
            _param = master_params[param_ref]
        if _param["name"] not in forbidden_params:
            output.append(_param)
    return output


def parameters_as_signature(params, master_params):
    output = ""
    for _param in trim_params(params, master_params):
        type_hint = get_type(_param)
        output += "%s: %s, " % (_param["name"], type_hint)
    output = output.rstrip(", ")
    return output


def parameters_as_docstring(params, master_params):
    output = []
    for _param in trim_params(params, master_params):
        output.append(
            "%s:\t%s%s\t\t%s" % (_param["name"], get_type(_param),
                                 ": " + _param["format"] if "format" in _param else "", _param["description"])
        )
    return output


def parameters_as_type_gates(params, master_params):
    output = []
    for _param in trim_params(params, master_params):
        output.append(parameter_as_type_gate(_param))
    return output


def parameter_as_type_gate(param, indent_level=2, param_name=""):
    if param_name == "":
        if "name" in param:
            param_name = param["name"]
        else:
            param_name = get_type(param)

    return """if type(%s) is not %s:
%sraise Exception("%s must be type %s!")""" % (
        param_name, get_type(param),
        " " * 4 * indent_level,
        param_name, get_type(param)
    )


def get_type(m):
    if "type" in m and m["type"] in swagger_py_type_lookup and "enum" not in m:
        return swagger_py_type_lookup[m["type"]]
    elif "name" in m:
        t = m["name"]
    elif "title" in m:
        t = m["title"]
    elif "description" in m:
        t = m["description"]
    elif "collectionFormat" in m:
        t = m["collectionFormat"]
    else:
        t = ""
    # Account for comma's
    # print(t)
    t = t.split(",")[0]
    # UpperCase each word
    t = t.replace("_", " ").title()
    # Remove Spaces, dashes, etc
    t = t.split(" ")[-1].replace(" ", "").replace("-", "_").replace("_", "")
    # Remove Junk Words
    while t.startswith("Post"):
        t = t[4:]
    while t.startswith("Get"):
        t = t[3:]
    return t
