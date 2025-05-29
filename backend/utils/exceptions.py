class ResumeParserError(Exception):
    """Base exception for resume parser errors"""
    pass

class PDFExtractionError(ResumeParserError):
    """Raised when there's an error extracting text from PDF"""
    pass

class APIError(ResumeParserError):
    """Raised when there's an error with the OpenRouter API"""
    pass

class JobScraperError(Exception):
    """Base exception for job scraper errors"""
    pass

class ScrapingError(JobScraperError):
    """Raised when there's an error scraping job data"""
    pass

class BrowserError(JobScraperError):
    """Raised when there's an error with the browser automation"""
    pass

class RateLimitError(JobScraperError):
    """Raised when the scraper hits rate limits"""
    pass 