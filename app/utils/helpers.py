from fastapi import UploadFile
import csv
from sqlalchemy.orm import Session
from fastapi import HTTPException
import pandas as pd
import io


async def parse_csv(file: UploadFile, table_name: str):
    """Parse CSV file into a list of dictionaries."""
    try:
        if file.content_type != 'text/csv':
            raise HTTPException(status_code=400, detail="Unsupported file type")
        records = []
        content = await file.read()
        if table_name == 'manuscripts':
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            df.rename(columns={'#': 'manuscript_id'}, inplace=True)
            selected_columns = ['manuscript_id', 'Title', 'Abstract']
            df = df[selected_columns]
            records = df.to_dict(orient='records')
            return records
        decoded_content = content.decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_content)
        for row in reader:
            records.append(row)
        return records
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while parsing CSV: {e}")
    

async def save_records_to_db(db: Session, model, records):
    try:
        for record in records:
            new_record = model(**record)
            if new_record.__dict__.get('reviewer_id')=='cation Method for Multiple Antenna':
                new_record.reviewer_id = 181
            db.add(new_record)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while saving records: {e}")