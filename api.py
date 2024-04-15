from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import asyncio
from uuid import uuid4
from utils import extract_restaurant_information
import uvicorn
from pydantic import BaseModel

from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

origins = ["*"]
app.add_middleware(
 CORSMiddleware,
 allow_origins=origins,
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

apify_client = ApifyClient(os.environ.get("APIFY_API_KEY"))

# Simple jobs dictionary to store
jobs = {}

# Location must be the full name of the location
class Location(BaseModel):
    location: str

@app.post("/restaurants/")
async def create_restaurant_job(location_data: Location):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "scraping"}
    asyncio.create_task(retrieve_restaurants(job_id, location_data.location))
    return {"job_id": job_id}

async def retrieve_restaurants(job_id, location):
    try:
        actor_call = await asyncio.to_thread(
            apify_client.actor('apify/instagram-scraper').call,
            run_input={
                "addParentData": False,
                "enhanceUserSearchWithFacebookPage": False,
                "isUserTaggedFeedURL": False,
                "resultsLimit": 3,
                "resultsType": "posts",
                "search": f"Restaurant in {location}",
                "searchLimit": 250,
                "searchType": "user"
                }
        )

        found_restaurants = apify_client.dataset(actor_call['defaultDatasetId']).list_items().items
        jobs[job_id]["status"]="parsing"

        tasks = [extract_restaurant_information(restaurant) for restaurant in found_restaurants if restaurant['isBusinessAccount']]
        results = await asyncio.gather(*tasks)

        
        # Filter out restaurants that opened within the last year and have a valid opening date
        filtered_restaurants = [
            restaurant for restaurant in results
            if restaurant['date_opened'] != "N/A" and
            datetime.now() - datetime.strptime(restaurant['date_opened'], '%Y-%m-%d') <= timedelta(days=365)
        ]
        # Sort by opening date
        sorted_restaurants = sorted(filtered_restaurants, key=lambda x: x['date_opened'], reverse=True)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["data"] = sorted_restaurants


    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.get("/jobs/{job_id}/")
def get_job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
