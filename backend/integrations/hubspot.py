import json
import secrets
import os
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from datetime import datetime
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from dateutil import parser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI')

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise ValueError("Missing required HubSpot environment variables")

SCOPES = 'oauth crm.objects.contacts.read'
authorization_url = f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}'

async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    """Retrieves contacts from HubSpot and converts them to IntegrationItems"""
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    
    # Get contacts from HubSpot
    response = requests.get(
        'https://api.hubapi.com/crm/v3/objects/contacts',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail='Failed to fetch HubSpot contacts')

    contacts = response.json().get('results', [])
    integration_items = []

    for contact in contacts:
        properties = contact.get('properties', {})
        created_at_str = contact.get('createdAt')
        updated_at_str = contact.get('updatedAt')
        created_at = parser.isoparse(created_at_str) if created_at_str else None
        updated_at = parser.isoparse(updated_at_str) if updated_at_str else None
        
        item = IntegrationItem(
            id=contact.get('id'),
            type='contact',
            name=f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip() or 'Unnamed Contact',
            creation_time=created_at,
            last_modified_time=updated_at,
            url=f"https://app.hubspot.com/contacts/{contact.get('id')}",
            visibility=True
        )
        integration_items.append(item)

    return integration_items

async def create_integration_item_metadata_object(response_json):
    # TODO
    pass