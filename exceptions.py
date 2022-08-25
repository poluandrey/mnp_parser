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


class SourceFileError(Error):
    """main error raised in case of error with source file"""
    pass


class SourceMnpFileNotExists(SourceFileError):
    """raise in case of source mnp file not exists"""
    pass


class SourceMnpFileIsEmpty(SourceFileError):
    """raise in case empty source file"""
    pass


class LatviaHandlingError(Error):
    """raise in case of error during parse Latvia file"""
    pass


class MoreThanOneSourceFilesFound(Error):
    """raise in case of more than one source files found"""
    pass


class LatviaParserError(Error):
    """raise in case parser error"""
    pass



