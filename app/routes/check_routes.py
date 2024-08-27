from fastapi import APIRouter, HTTPException, Body
from ._models import checkImages
import base64
from ..controllers.check_controller import checkController

router = APIRouter()

@router.post("/check-image")
async def checkImages(body: checkImages):
    try:
        result=checkController.checkImages(body.empID,body.images)
        if result:
            return {"message": "Image uploaded successfully", "status": 200,"data":result}
        else:
            return {"status": 500, "message": "Internal Server Error"}
    except Exception as err:
        print(f"Error in check Router",err)
        raise HTTPException(status_code=400, detail="Internal Server Error")
