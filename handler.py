from kubernetes_utility import KubernetesUtility
from schemas import CertificateSchema, OwnerReferenceSchema

class CertificateHandler:
    def __init__(self):
        self.kubernetes_utility = KubernetesUtility()
        self.certificate_data = {}

    def create_certificate(self, gateway_schema: dict):
        try:
            gateway_metadata = gateway_schema["metadata"]
            self._handle_annotations(gateway_metadata["annotations"])
            gateway_spec = gateway_schema["spec"]
            owner_reference = OwnerReferenceSchema(
                name=gateway_metadata["name"],
                uid=gateway_metadata["uid"]
            )
            certificate = CertificateSchema(
                namespace=gateway_metadata["namespace"],
                name=gateway_spec["servers"][0]["tls"]["credentialName"],
                dns_names=gateway_spec["servers"][0]["hosts"],
                duration=self.certificate_data["duration"],
                renew_before=self.certificate_data["renew_before"],
                issuer_name=self.certificate_data["issuer_name"],
                issuer_kind=self.certificate_data["issuer_kind"],
                secret_name=gateway_spec["servers"][0]["tls"]["credentialName"]
            )
            if self.kubernetes_utility.get_certificate(certificate.name, certificate.namespace):
                self.kubernetes_utility.update_certificate(certificate, owner_reference)
            else:
                self.kubernetes_utility.create_certificate(certificate, owner_reference)
        except Exception as e:
            raise e

    def _handle_annotations(self, gateway_annotations: dict):
        issuer = gateway_annotations.get("cert-manager.io/issuer")
        cluster_issuer = gateway_annotations.get("cert-manager.io/cluster-issuer")

        if issuer:
            self.certificate_data["issuer_name"] = issuer
            self.certificate_data["issuer_kind"] = "Issuer"
        elif cluster_issuer:
            self.certificate_data["issuer_name"] = cluster_issuer
            self.certificate_data["issuer_kind"] = "ClusterIssuer"
        else:
            raise ValueError("Gateway must have either 'cert-manager.io/issuer' or 'cert-manager.io/cluster-issuer' annotation")
        self.certificate_data["duration"] = gateway_annotations.get("cert-manager.io/duration", "4320h")
        self.certificate_data["renew_before"] = gateway_annotations.get("cert-manager.io/renew-before", "360h")
