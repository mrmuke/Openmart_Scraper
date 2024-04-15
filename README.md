# Description
A FastAPI endpoint to retrieve the newest opened restaurants in a given location.

# Running Locally
Create a .env file with APIFY_API_KEY and OPENAI_API_KEY.
```
pip install -r requirements.txt
```
```
python api.py
```

# Demo
```
curl --location 'http://3.128.255.241/restaurants/' \
--header 'Content-Type: application/json' \
--data '{
    "location":"NY"
}'
```
```
curl --location 'http://3.128.255.241/jobs/{job_id}'
```
* Insert job id returned from previous request
