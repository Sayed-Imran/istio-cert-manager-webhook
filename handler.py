from kubernetes_utility import KubernetesUtility
from schemas import CertificateSchema, OwnerReferenceSchema
from errors import AnnotationDoesNotExist
from config import CertificateConfig
import logging

class CertificateHandler:
    def __init__(self, request_object: dict):
        try:
            self.request_object = request_object
            self.kubernetes_utility = KubernetesUtility()
            self.certificate_data = {}
            self._handle_annotations(request_object["metadata"]["annotations"])
        except AnnotationDoesNotExist as e:
            logging.info(f"Annotation does not exist, hence skipping certificate creation")
        except Exception as e:
            raise e

    def create_certificate(self):
        try:
            gateway_metadata = self.request_object["metadata"]
            # self._handle_annotations(gateway_metadata["annotations"])
            gateway_spec = self.request_object["spec"]
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
                logging.info(f"Certificate {certificate.name} already exists, updating it")
            else:
                self.kubernetes_utility.create_certificate(certificate, owner_reference)
                logging.info(f"Certificate {certificate.name} created successfully")
        except AnnotationDoesNotExist as e:
            logging.info(f"Annotation does not exist, hence skipping certificate creation")
        except Exception as e:
            raise e

    def _handle_annotations(self, gateway_annotations: dict):
        issuer = gateway_annotations.get("cert-manager.io/issuer")
        cluster_issuer = gateway_annotations.get("cert-manager.io/cluster-issuer")

        if issuer:
            logging.info(f"Using Issuer: {issuer}")
            self.certificate_data["issuer_name"] = issuer
            self.certificate_data["issuer_kind"] = "Issuer"
            self.kubernetes_utility.get_issuer(issuer, self.request_object["metadata"]["namespace"])
        elif cluster_issuer:
            logging.info(f"Using ClusterIssuer: {cluster_issuer}")
            self.certificate_data["issuer_name"] = cluster_issuer
            self.certificate_data["issuer_kind"] = "ClusterIssuer"
            self.kubernetes_utility.get_cluster_issuer(cluster_issuer)
        else:
            raise AnnotationDoesNotExist("Gateway must have either 'cert-manager.io/issuer' or 'cert-manager.io/cluster-issuer' annotation")
        self.certificate_data["duration"] = gateway_annotations.get("cert-manager.io/duration", CertificateConfig.duration)
        self.certificate_data["renew_before"] = gateway_annotations.get("cert-manager.io/renew-before", CertificateConfig.renew_before)
