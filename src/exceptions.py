class PipelineError(Exception):
    pass


class PDFReadError(PipelineError):
    pass


class AIExtractionError(PipelineError):
    pass


class ExcelWriteError(PipelineError):
    pass


class ConfigError(PipelineError):
    pass
