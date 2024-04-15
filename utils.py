from datetime import datetime
from htmldate import find_date
from openai import OpenAI
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()

import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def extract_restaurant_information(restaurant):
    # Strategies for extracting each restaurant information
    # Find Opening Date: 
            # - look through posts to find grand opening captions with LLM
            # - otherwise get the date the site was published as approximate indication of date
            # - otherwise date of first instagram post
            # - else no opening date could be found
        # Restaurant Name
            # - pass in username, full name, biography to LLM
            # - all post captions as context if full name is not mentioned in above
            # - else no restaurant name could be found
        # Restaurant Category/Cuisine
            # - pass in biography, post captions to LLM
            # - maybe: search for cuisine in business category?
            # - otherwise no restaurant cuisine can be found
        # Address
            # - biography, post captions to LLM
            # - maybe: otherwise search for location ids in posts location?
            # - else no cuisine could be found

    # Example Output: 
    # {   "name": "Gourmet Bites",
    #     "category": "Italian",
    #     "date_opened": "2023-09-01",
    #     "address": "123 Flavor St, San Francisco",
    # }


    # Collecting post caption aggregate string
    caption_number = 1
    captions = []
    for post in restaurant['latestPosts']:
            caption_text = f"Post Caption {caption_number}:\n{post['caption']}"
            captions.append(caption_text)
            caption_number += 1

    all_captions = "\n".join(captions)
    
    # Other relevant properties
    bio = restaurant['biography']
    full_name = restaurant['fullName']
    business_url = restaurant['externalUrl'] if 'externalUrl' in restaurant else None

    # Rate limit handling and extraction prompt
    while True:
        try:
            response =  await asyncio.to_thread(client.chat.completions.create,
            model="gpt-4",
            messages=[{"role": "system", "content": "You are data extractor GPT that extracts structured JSON values from various information taken from a restaurants' IG (Instagram) page."},
            {"role": "user", "content": f'''
            Here is information taken from the restaurants' instagram page:
            'Restaurant IG Name: {full_name}
            Restaurant IG Bio: {bio}
            Restaurant Post Captions:
            {all_captions}'

            Now, extract the name, cuisine/category, date opened, and address of the restaurant and give an output using the exact following JSON format:
            {{
            "name": "Gourmet Bites",
            "category": "Italian",
            "date_opened": "2023-09-01",
            "address": ["123 Flavor St, San Francisco"]
            }}
            Restaurants can have multiple addresses/locations, but if you can't find one put an empty array. If there is no month or day fill in 01 for them. For the other properties, if you cannot find their values, put "N/A" instead of the value.
            '''}],
            temperature=0.0
            )
            response = response.choices[0].message.content
        
            break
        except:
            print("rate limit exceeded")
            await asyncio.sleep(10)
    json_response_start = response.index('{')
    json_response_end = response.index('}')

    json_response = response[json_response_start:json_response_end+1]
    try:
        response_dict = json.loads(json_response)
    except:
        print("bad json")
        print(response)

    # Try to find opening date in website metadata if not found on instagram
    try:
        if(response_dict["date_opened"]=="N/A" and business_url!=None):
            website_publish_date = find_date(business_url)
            if(website_publish_date!=None):
                response_dict["date_opened"] = website_publish_date # use restaurant website publish date as backup in case not mentioned
    except:
        pass

    response_dict['social_media_post_url'] = restaurant['latestPosts'][0]['url']

    return response_dict
    