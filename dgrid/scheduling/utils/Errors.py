"""
Custom Exceptions for DGrid classes
"""


class HostValueError(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)


class InteractiveContainerNotSpecified(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class RemoteExecutionError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ProcessIdRetrievalFailure(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)