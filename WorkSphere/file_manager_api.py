# API to upload and extract data from Databases (PostgreSQL and MongoDB)
from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.responses import FileResponse
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
import aiofiles
import os
import uuid
from datetime import datetime

router = APIRouter()
app = FastAPI(title="Uploading and Extracting Data")

# Creating PostgreSQL Engine
pg_engine = create_engine("postgresql://postgres:pr1t81m@localhost:5432/flight_delays")

# Creating MongoDB Client
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["database"]
mongo_collection = mongo_db["collection"]

# Folder to store exports temporarily
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

@router.get("/", tags=["File Manager"])
def get_files():
    return {"message": "Welcome to File Manager API"}

# endpoint to upload file in Database
@router.post("/upload", tags=["File Manager"])
async def upload_file(file: UploadFile = File(...)):
    try:
        temp_path = f"temp_{uuid.uuid4().hex}_{os.path.basename(file.filename)}"

        # Saving file temporarily
        async with aiofiles.open(temp_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1 MB chunks
                await f.write(chunk)

        # Reading file with pandas
        if file.filename.endswith(".csv"):
            chunks = pd.read_csv(temp_path, chunksize=10000)
        else:
            chunks = [pd.read_excel(temp_path)]

        total_rows = 0
        columns = None

        for chunk in chunks:
            total_rows += len(chunk)
            if columns is None:
                columns = list(chunk.columns)

            # Saving into PostgreSQL
            chunk.to_sql("mytable", pg_engine, if_exists="append", index=False)

            # Saving into MongoDB in batches
            docs = chunk.to_dict(orient="records")
            batch_size = 1000
            for i in range(0, len(docs), batch_size):
                mongo_collection.insert_many(docs[i:i + batch_size])

        os.remove(temp_path)

        return {
            "message": f"Data from {file.filename} uploaded successfully!",
            "rows": total_rows,
            "columns": columns
        }

    except Exception as e:
        return {"error": str(e)}

# endpoint to export file from sql DB
@router.get("/export/sql", tags=["File Manager"])
def export_sql():
    try:
        df = pd.read_sql("SELECT * FROM mytable", pg_engine)
        filename = f"export_sql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(EXPORT_FOLDER, filename)
        df.to_excel(filepath, index=False)

        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        return {"error": str(e)}

# endpoint to export file from mongoDB
@router.get("/export/mongo", tags=["File Manager"])
def export_mongo():
    try:
        data = list(mongo_collection.find({}, {"_id": 0}))
        if not data:
            return {"message": "No data found in MongoDB"}

        df = pd.DataFrame(data)
        filename = f"export_mongo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(EXPORT_FOLDER, filename)
        df.to_csv(filepath, index=False)

        return FileResponse(
            path=filepath,
            media_type="text/csv",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        return {"error": f"MongoDB export failed: {str(e)}"}
