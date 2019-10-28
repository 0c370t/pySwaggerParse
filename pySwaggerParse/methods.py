from pathlib import Path

from pySwaggerParse.helpers import get_http_method, parameters_as_signature, \
    parameters_as_docstring, parameters_as_type_gates


def create(namespaces, root_path, swagger_definition):
    # Create one file per namespace, with one method per endpoint
    root_path.mkdir(parents=True, exist_ok=True)
    for namespace in namespaces.keys():
        # Create file
        namespace_path = Path(root_path, Path(namespace + ".py"))
        namespace_path.touch(exist_ok=True)
        with open(namespace_path, "w") as namespace_file:
            # Write module docstring
            docstring = """\"\"\"
    This file was automatically generated.
    %s.py is designed to provide a programmatic interface to the %s namespace of %s
\"\"\"
from ..models import *

""" % (namespace, namespace, swagger_definition["info"]["title"])
            namespace_file.writelines(docstring)
            for path_obj in namespaces[namespace]:
                path = path_obj["path"]
                http_method = get_http_method(path_obj)
                path_specifics = path_obj[http_method]
                # Write method with as descriptive a docstring as possible
                print(http_method)
                print(path_specifics["parameters"]) if "parameters" in path_specifics else print("No params for this method")
                method_boilerplate = """
def %s(%s):
    \"\"\"
        This method reflects the %s: '%s' endpoint.
        Swagger Description:
             %s
        Parameter Descriptions:
            %s
    \"\"\"
    %s
    pass

""" % (
                    path_specifics["operationId"],
                    parameters_as_signature(path_specifics['parameters'],
                                            swagger_definition["parameters"]),
                    http_method.upper(),
                    path,
                    ".\n".join(path_specifics["description"].split(".")).replace("\n", "\n            "),
                    "\n            ".join(parameters_as_docstring(path_specifics["parameters"],
                                                                  swagger_definition["parameters"])),
                    "\n    ".join(
                        parameters_as_type_gates(path_specifics["parameters"], swagger_definition["parameters"]))
                )
                namespace_file.write(method_boilerplate)
