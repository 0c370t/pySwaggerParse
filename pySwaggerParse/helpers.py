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


def extract_parameters_as_signature_string(params, master_params):
    output = ""
    for _param in trim_params(params, master_params):
        type_hint = ""
        if "type" in _param:
            type_hint += get_type(_param)
        else:
            type_hint += "object"
        output += "%s: %s, " % (_param["name"], type_hint)
    output = output.rstrip(", ")
    return output


def extract_parameters_as_docstring_lines(params, master_params):
    output = []
    for _param in trim_params(params, master_params):
        output.append(
            "%s:\t%s%s\t\t%s" % (_param["name"], _param["type"] if "type" in _param else "object",
                                 ": " + _param["format"] if "format" in _param else "", _param["description"])
        )
    return output


def get_type(m):
    t = ""
    if "type" in m and m["type"] in swagger_py_type_lookup and "enum" not in m:
        return swagger_py_type_lookup[m["type"]]
    elif "title" in m:
        t = m["title"]
    elif "description" in m:
        t = m["description"]
    else:
        t = ""
    # Account for comma's
    t = t.split(",")[0]
    # UpperCase each word
    t = t.replace("_", " ").title()
    # Remove Spaces, dashes, etc
    t = t.replace(" ", "").replace("-","_")
    # Remove Junk Words
    t = t.lstrip("Post").lstrip("get")
    return t

