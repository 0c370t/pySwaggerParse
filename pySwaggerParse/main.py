import json
from pathlib import Path
from pySwaggerParse import methods, models


def main(input_path, output_path):
    # File parsing
    swagger_file = open(input_path)
    swagger_json = swagger_file.read()
    swagger = json.loads(swagger_json)

    namespaces = {}
    # Extract namespaces
    # i.e. /api/{namespace}/{path}
    for endpoint in swagger["paths"]:
        endpoint_fragments = endpoint.split("/")
        if endpoint_fragments[1] not in namespaces.keys():
            namespaces[endpoint_fragments[1]] = []
        path_metadata = swagger["paths"][endpoint]
        path_metadata["path"] = endpoint
        namespaces[endpoint_fragments[1]].append(path_metadata)

    # Create output directory
    root_path = Path(output_path)
    root_path.mkdir(parents=True, exist_ok=True)
    # Create Parameter -> Model Relation
    models.create(swagger, Path(root_path, "models.py"))
    # Create Endpoint -> Method Relation
    methods.create(namespaces, Path(root_path, "methods"), swagger)


main("ESI.json", "esi/api")
