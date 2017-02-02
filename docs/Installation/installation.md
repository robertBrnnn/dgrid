# Building Dgrid

To build DGrid run the following (must be run from the root directory of the project):
`python setup.py bdist_wheel`

The DGrid .whl package will be inside the created dist directory

Specific configuration instructions for schedulers are available [here](../)
...and should be followed ;-)

# Installation
To install DGrid run:
`pip install DGrid-VERSION_NUMBER_HERE-py2-none-any.whl` where VERSION_NUMBER_HERE is the version number of the built .whl package.

Dgrid will be installed to your Python package directory.

__Note__
The DGrid scripts directory containning shell scripts used during execution will be in your Python package directory at /Your/Python/Pakage_dir/dgrid-scripts
