import os, requests


def triggerSensor(name, state, logger):
    
    logger.debug(f'Bearer {os.environ["SUPERVISOR_TOKEN"]}')
    headers = {
        'Authorization': f'Bearer {os.environ["SUPERVISOR_TOKEN"]}',
        "content-type": "application/json"
    }

    entity = {
        "state": state,
        #"state_class": "measurement",
        "attributes": {
            "friendly_name": name, 
        }
    }
    
    logger.debug(f'posting to http://supervisor/core/api/states/{name}')
    
    response = requests.post(f'http://supervisor/core/api/states/{name}', headers=headers, json = entity)#, timeout=3)
    if( not response.ok):
        logger.error(f'failed to trigger {name} Error: {response.text}')

    logger.debug(response)
    return response.ok