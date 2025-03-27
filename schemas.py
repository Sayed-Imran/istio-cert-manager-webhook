from pydantic import BaseModel

class CertificateSchema(BaseModel):
    namespace: str
    name: str
    secret_name: str
    issuer_name: str
    issuer_kind: str
    dns_names: list[str]
    duration: str   = "4320h"
    renew_before: str   = "360h"

class OwnerReferenceSchema(BaseModel):
    api_version: str = "networking.istio.io/v1"
    kind: str = "Gateway"
    name: str
    uid: str
    controller: bool = True
    block_owner_deletion: bool = True
