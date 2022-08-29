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


class MoreThanOneSourceFilesFound(SourceFileError):
    """raise in case of more than one source files found"""
    pass


class BadSourceZipFile(SourceFileError):
    """raise in case of more or less one file in the zip archive found"""
    pass


class LatviaFileHandlingError(Error):
    """raise in case of error during parse Latvia file"""
    pass


class LatviaParserError(Error):
    """raise in case parser error"""
    pass


class BelarusParserError(Error):
    """raise in case parser error"""
    pass


class BelarusFileHandlingError(Error):
    """raise in case file handling error"""
    pass


class ParserError(Error):
    """raise in case parser error"""
    pass


class MnpProcessingError(Error):
    """raise in case file handling error"""
    pass
