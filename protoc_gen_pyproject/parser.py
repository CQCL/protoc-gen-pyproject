import os.path
import re
from pathlib import Path
from typing import TypedDict

import toml
import dunamai
from betterproto.lib.google.protobuf.compiler import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
    CodeGeneratorResponseFile,
)

PARAM_REGEX = re.compile(
    r"(?:(?P<param>[^,=]+)(?:=(?P<key>[^,=]+)(?:=(?P<value>(?:[^,\\]|\\,|\\\\)+))?)?)"
)


class ParamValue(TypedDict):
    key: str
    value: str | None


Params = dict[str, ParamValue | None]


def parse_params(params_str: str) -> Params:
    """Parse the parameters string into a structured form.

    >>> parse_params("g1,g2=k2,g3=k3=v3")
    {'g1': None, 'g2': {'key': 'k2'}, 'g3': {'key': 'k3', 'value': 'v3'}}
    """
    params = {}
    for match in PARAM_REGEX.finditer(params_str):
        name = match.group("param")
        key = match.group("key")
        if key is None:
            params[name] = None
        else:
            value = match.group("value")
            if value is None:
                params[name] = {"key": key}
            else:
                params[name] = {"key": key, "value": value}

    return params


def generate_code(request: CodeGeneratorRequest) -> CodeGeneratorResponse:
    """Create a response to generate the project file.

    Will look at the `gen_project` parameter if set to decide which
    file to use.
    """
    params = parse_params(request.parameter)

    file_path = "pyproject.toml"
    generate_pyproject_param = params.get("gen_pyproject")
    if generate_pyproject_param is not None:
        file_path = generate_pyproject_param["key"]

    if not os.path.exists(file_path):
        return CodeGeneratorResponse(error=f"No project file found at '{file_path}'")

    file_content = None
    with open(file=file_path) as f:
        file_content = f.read()

    # Automatically set package version if configured to do so.
    set_version_from_vcs = params.get("set_version_from_vcs")
    if set_version_from_vcs is not None:
        pyproject_toml = toml.loads(file_content)
        pyproject_toml["version"] = dunamai.Version.from_any_vcs()
        file_content = toml.dumps(pyproject_toml)

    files = [CodeGeneratorResponseFile(name="pyproject.toml", content=file_content)]

    include_py_typed = params.get("include_py_typed")
    if include_py_typed is None or (
        include_py_typed is not None and include_py_typed["key"] != "False"
    ):
        package_name = params.get("package_name")
        if package_name is None:
            return CodeGeneratorResponse(
                error=f"package_name must be set if `include_py_typed` is True."
            )

        files.append(
            CodeGeneratorResponseFile(
                name=str(Path(package_name["key"]) / "py.typed"), content=""
            )
        )

    response = CodeGeneratorResponse(file=files)
    return response
