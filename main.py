from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import Request
import logging
from handler import CertificateHandler
from schemas import ControllerResponseSchema, AdmissionResponseSchema


app = FastAPI()


@app.post("/validate")
async def validate(request: Request, bg_tasks: BackgroundTasks):
    try:
        data = await request.json()
        certificate_handler = CertificateHandler(data["request"]["object"])
        bg_tasks.add_task(
            certificate_handler.create_certificate
        )
        response =  ControllerResponseSchema(
            response= AdmissionResponseSchema(
                uid=data["request"]["uid"],
                allowed=True,
                status={
                    "message": "Validation passed",
                }
            )
        )
        logging.info(f"Response: {response}")
        return response

    except Exception as e:
        logging.error(f"Error validating data: {e}")
        return ControllerResponseSchema(
            response= AdmissionResponseSchema(
                uid=data["request"]["uid"],
                allowed=False,
                status={
                    "message": str(e),
                }
            )
        )
