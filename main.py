from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request
import logging
from handler import CertificateHandler
from schemas import ControllerResponseSchema, AdmissionResponseSchema


app = FastAPI()
logging.basicConfig(level=logging.INFO)


@app.post("/validate")
async def validate(request: Request):
    allowed = True
    try:
        certificate_handler = CertificateHandler()
        data = await request.json()
        certificate_handler.create_certificate(data["request"]["object"])
        response =  ControllerResponseSchema(
            apiVersion="admission.k8s.io/v1",
            kind="AdmissionReview",
            response= AdmissionResponseSchema(
                uid=data["request"]["uid"],
                allowed=allowed,
                status={
                    "message": "Validation passed",
                }
            )
        )
        logging.info(f"Response: {response}")
        return response

    except Exception as e:
        logging.error(f"Error validating data: {e}")
        allowed = False
        return JSONResponse(
            {
                "allowed": allowed,
                "uid": data["request"]["uid"],
                "status": {
                    "message": "Validation failed",
                }
            }
        )
