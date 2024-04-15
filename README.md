# Openmart_Scraper
API endpoint that extracts relevant restaurant information from new restaurants in a given location.

# Steps to Run Locally
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
curl --location 'http://3.128.255.241/jobs/{job_id}'`
```
*Insert job id returned from previous request
