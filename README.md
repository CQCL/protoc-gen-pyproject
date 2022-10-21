# protoc-gen-pyproject

A basic protoc plugin to generate a pyproject file for generated code.

## Example usage with buf

```yaml
version: v1
managed:
  enabled: true
plugins:
  - name: python_betterproto
    out: gen/python/quantinuumapis/quantinuumapis
    strategy: all # Required to prevent duplicate file generation
    opt:
      - --proto3-optional
  - name: pyproject
    out: gen/python/quantinuumapis
    strategy: all # Required to prevent duplicate file generation
    opt:
      - gen_pyproject=templates/pyproject.toml.template
```
