from kubernetes import config, client
from schemas import CertificateSchema, OwnerReferenceSchema


class KubernetesUtility:
    def __init__(self):
        config.load_config()
        self.client = client.CustomObjectsApi()
        self.custom_object_group = 'cert-manager.io'
        self.custom_object_version = 'v1'
        self.custom_object_plural = 'certificates'

    def create_certificate(self, certificate: CertificateSchema, owner_reference: OwnerReferenceSchema):
        certificate = {
            "apiVersion": f"{self.custom_object_group}/{self.custom_object_version}",
            "kind": "Certificate",
            "metadata": {
                "name": certificate.name,
                "ownerReferences": [owner_reference.model_dump()]
            },
            "spec": {
                "secretName": certificate.secret_name,
                "duration": certificate.duration,
                "renewBefore": certificate.renew_before,
                "dnsNames": certificate.dns_names,
                "usages" : [
                    "digital signature",
                    "key encipherment",
                ],
                "issuerRef": {
                    "name": certificate.issuer_name,
                    "kind": certificate.issuer_kind,
                    "group": f"{self.custom_object_group}/{self.custom_object_version}"
                }
            }
        }
        self.client.create_namespaced_custom_object(
            self.custom_object_group,
            self.custom_object_version,
            certificate.namespace,
            self.custom_object_plural,
            certificate
        )
