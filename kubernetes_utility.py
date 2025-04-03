from kubernetes import config, client
from kubernetes.client.exceptions import ApiException
from schemas import CertificateSchema, OwnerReferenceSchema
from errors import IssuerDoesnotExist, ClusterIssuerDoesnotExist
import logging

class KubernetesUtility:
    def __init__(self):
        config.load_config()
        self.client = client.CustomObjectsApi()
        self.custom_object_group = 'cert-manager.io'
        self.custom_object_version = 'v1'
        self.custom_object_plural = 'certificates'

    def get_certificate(self, name, namespace):
        try:
            return self.client.get_namespaced_custom_object(
                self.custom_object_group,
                self.custom_object_version,
                namespace,
                self.custom_object_plural,
                name
            )
        except ApiException as e:
            if e.status == 404:
                return None
            raise

    def create_certificate(self, certificate: CertificateSchema, owner_reference: OwnerReferenceSchema):
        certificate_body = {
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
                    "group": self.custom_object_group
                }
            }
        }
        self.client.create_namespaced_custom_object(
            self.custom_object_group,
            self.custom_object_version,
            certificate.namespace,
            self.custom_object_plural,
            certificate_body
        )

    def update_certificate(self, certificate: CertificateSchema, owner_reference: OwnerReferenceSchema):
        certificate_data = {
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
                    "group": self.custom_object_group
                }
            }
        }
        self.client.replace_namespaced_custom_object(
            self.custom_object_group,
            self.custom_object_version,
            certificate.namespace,
            self.custom_object_plural,
            certificate.name,
            certificate_data
        )

    def get_issuer(self, name, namespace):
        try:
            return self.client.get_namespaced_custom_object(
                self.custom_object_group,
                self.custom_object_version,
                namespace,
                'issuers',
                name
            )
        except ApiException as e:
            logging.error(f"Error fetching issuer: {e}")
            if e.status == 404:
                raise IssuerDoesnotExist(f"Issuer {name} does not exist in namespace {namespace}")

    def get_cluster_issuer(self, name):
        try:
            return self.client.get_cluster_custom_object(
                self.custom_object_group,
                self.custom_object_version,
                'clusterissuers',
                name
            )
        except ApiException as e:
            logging.error(f"Error fetching cluster issuer: {e}")
            if e.status == 404:
                raise ClusterIssuerDoesnotExist(f"ClusterIssuer {name} does not exist")
