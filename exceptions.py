class Error(Exception):
    """Base class for other exceptions"""
    pass


class ConfigLoadError(Error):
    """raise in case error during load config"""
    pass


class CreateConfigDirError(Error):
    """
    raise in case of error during creating not existing
    directory specified in settings"""
    pass


class SourceMnpFileNotExists(Error):
    """raise in case of source mnp file not exists"""
    pass
