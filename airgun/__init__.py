import re

from airgun.settings import Settings

settings = Settings()

ERRATA_REGEXP = re.compile(r"\w{3,4}[:-]\d{4}[-:]\d{1,4}")
