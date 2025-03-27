from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
import logging


app = FastAPI()
logging.basicConfig(level=logging.INFO)


@app.post("/validate")
async def validate(request: Request):
    allowed = True
    try:
        data = await request.json()
        logging.info(f"Validating data: {data}")
        response =  {
            "apiVersion": "admission.k8s.io/v1",
             "kind": "AdmissionReview",
            "response" : {
                "allowed": allowed,
                "uid": data["request"]["uid"],
                "status": {
                    "message": "Validation passed",
                }
            }
        }
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
