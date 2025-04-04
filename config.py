from pydantic import field_validator
from pydantic_settings import BaseSettings


class _CertificateConfig(BaseSettings):
    duration: str = "4320h"
    renew_before: str = "360h"

    @field_validator("duration", "renew_before")
    def validate_duration(cls, value: str) -> str:
        if not value.endswith("h"):
            raise ValueError("DURATION and RENEW_BEFORE must end with 'h'")
        return value


CertificateConfig = _CertificateConfig()
