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
* Note: Currently scraped results are limited to 50 to reduce concurrent load on GPT, but can be extended to up to 250 for more high-quality results

# Demo
```
curl --location 'http://3.128.255.241/api/restaurants/' \
--header 'Content-Type: application/json' \
--data '{
    "location":"NY"
}'
```
```
curl --location 'http://3.128.255.241/api/jobs/{job_id}'
```
* Insert job id returned from previous request
