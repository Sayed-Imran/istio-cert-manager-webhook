from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import Request
import logging
from handler import CertificateHandler
from schemas import ControllerResponseSchema, AdmissionResponseSchema


app = FastAPI()


@app.post("/validate")
async def validate(request: Request, bg_tasks: BackgroundTasks):
    allowed = True
    try:
        certificate_handler = CertificateHandler()
        data = await request.json()
        bg_tasks.add_task(
            certificate_handler.create_certificate,
            data["request"]["object"]
        )
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
