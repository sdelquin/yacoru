# https://docs.astral.sh/uv/guides/package/#publishing-your-package

# Clean temporary files
clean:
    rm -fr build dist *egg* *cache*

# Build project
build: clean
    uv build

# Upload to Test PyPI
upload-test: build
    uv publish -t $TESTPYPI_TOKEN --publish-url "https://test.pypi.org/legacy/"

# Upload to PyPI
upload: build
    uv publish -t $PYPI_TOKEN

# Open project url at Test PyPI
open-testpypi:
    open https://test.pypi.org/project/yacoru/

# Open project url at PyPI
open-pypi:
    open https://pypi.org/project/yacoru/

# Open iPython shell
sh:
    uv run ipython

# Bump version: component = [major, minor, patch]
bump component:
    uv version --bump {{component}}
