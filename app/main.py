from fastapi import FastAPI, Depends,UploadFile, File, Form
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.database import engine, get_db, create_tables
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks
from app.models import table_name_to_model
from app.utils.helpers import parse_csv, save_records_to_db
from app.utils.background_task import populate_paper_reviews
from app.utils.keyphrases import extract_keyphrases
from app.utils.similarity import extract_similarities


origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
    "http://localhost:8081",
    "*"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(background_job, 'interval', hours=6)
    # scheduler.start()
    create_tables()
    # try:
    yield
    # finally:
        # scheduler.shutdown()

app = FastAPI(lifespan=lifespan,
              title="DAIICT FastAPI",
              version="1.0.0",
              description="API's",
              docs_url="/docs",
              redoc_url="/redocs",
              )


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_table_names_from_engine():
    insp = inspect(engine)
    return insp.get_table_names()


@app.get("/", response_class=RedirectResponse,include_in_schema=False)
async def docs():
    return RedirectResponse(url="/docs")


@app.get("/api/tables")
async def get_table_list():
    try:
        insp = inspect(engine)
        table_names = insp.get_table_names()
        result = []
        for table in table_names:
            json_table = {"name": table}
            json_table['columns'] = [column.get('name') for column in insp.get_columns(table)]
            result.append(json_table)
    except Exception as e:
        print("Not able to find tables")
    return {
        "data": result, 
        "error": None
    }


@app.post('/api/extract/')
async def populate_table(background_tasks: BackgroundTasks, table_name:str = Form(...), file: UploadFile = File(...),db: Session = Depends(get_db)):
    try:
        if table_name not in table_name_to_model:
            raise HTTPException(status_code=404, detail=f"Schema for {table_name} is Invalid.")
        
        model = table_name_to_model[table_name]
        
        records = await parse_csv(file, table_name)

        await save_records_to_db(db, model, records)
        
        if table_name in ['reviewers', 'papers']:
            background_tasks.add_task(populate_paper_reviews, db)
            background_tasks.add_task(extract_keyphrases, db, 'reviewers_keyphrases')
        else:
            background_tasks.add_task(extract_keyphrases, db, 'manuscripts_keyphrases')
            
        background_tasks.add_task(extract_similarities, db)

        return {
            "status": "success",
            "status_code": 200,
            "message": f"{(table_name)} task started successfully."
        }
        
    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
                
                
