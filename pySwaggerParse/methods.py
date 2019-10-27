from pathlib import Path

from pySwaggerParse.helpers import get_http_method, extract_parameters_as_signature_string, \
    extract_parameters_as_docstring_lines


def create(namespaces, root_path, swagger_definition):
    # Create one file per namespace, with one method per endpoint
    root_path.mkdir(parents=True, exist_ok=True)
    for namespace in namespaces.keys():
        # Create file
        namespace_path = Path(root_path, Path(namespace + ".py"))
        namespace_path.touch(exist_ok=True)
        with open(namespace_path, "w") as namespace_file:
            # Write module docstring
            namespace_file.write("from ..models import *\n")
            docstring = """\"\"\"
    This file was automatically generated.
    %s.py is designed to provide a programmatic interface to the %s namespace of %s
\"\"\"

            """ % (namespace, namespace, swagger_definition["info"]["title"])
            namespace_file.writelines(docstring)
            for path_obj in namespaces[namespace]:
                path = path_obj["path"]
                http_method = get_http_method(path_obj)
                path_specifics = path_obj[http_method]
                # Write method with as descriptive a docstring as possible
                method_boilerplate = """
def %s(%s):
    \"\"\"
        This method reflects the %s: '%s' endpoint.
        Swagger Description:
            %s
        Parameter Descriptions:
            %s
    \"\"\"
    pass

""" % (
                    path_specifics["operationId"],
                    extract_parameters_as_signature_string(path_specifics['parameters'],
                                                           swagger_definition["parameters"]),
                    http_method.upper(), path,
                    path_specifics["description"].replace("\n", "\n            "),
                    "\n            ".join(extract_parameters_as_docstring_lines(path_specifics["parameters"],
                                                                                swagger_definition["parameters"]))
                )
                namespace_file.write(method_boilerplate)
