import sys

from betterproto.lib.google.protobuf.compiler import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
)

from .parser import generate_code


def main() -> None:
    """The plugin's main entry point.

    Follows the same structure as betterproto
    """

    data = sys.stdin.buffer.read()

    request = CodeGeneratorRequest()
    request.parse(data)

    response: CodeGeneratorResponse = generate_code(request)

    output = response.SerializeToString()

    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
