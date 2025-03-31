from pydantic import BaseModel
from config import CertificateConfig

class CertificateSchema(BaseModel):
    namespace: str
    name: str
    secret_name: str
    issuer_name: str
    issuer_kind: str
    dns_names: list[str]
    duration: str
    renew_before: str

class OwnerReferenceSchema(BaseModel):
    apiVersion: str = "networking.istio.io/v1"
    kind: str = "Gateway"
    name: str
    uid: str
    controller: bool = True
    blockOwnerDeletion: bool = True

class AdmissionResponseSchema(BaseModel):
    allowed: bool
    uid: str
    status: dict = {
        "message": "Validation passed",
    }
class ControllerResponseSchema(BaseModel):
    apiVersion: str = "admission.k8s.io/v1"
    kind: str = "AdmissionReview"
    response: AdmissionResponseSchema