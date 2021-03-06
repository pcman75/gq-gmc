import os, requests, numbers


def triggerSensor(name, friendly_name, seial_number, state, logger):
    
    logger.debug(f'Bearer {os.environ["SUPERVISOR_TOKEN"]}')
    headers = {
        'Authorization': f'Bearer {os.environ["SUPERVISOR_TOKEN"]}',
        "content-type": "application/json"
    }

    if(isinstance(state, numbers.Number)):
        logger.debug("state is numeric")
        entity = {
            "state": state,
            #"unique_id": str(seial_number),
            "attributes": {
                "friendly_name": friendly_name,
                "state_class": "measurement",
                "native_value": "float" 
            }
        }
    else:
        logger.debug("state is not numeric")
        entity = {
            "state": state,
            #"unique_id": str(seial_number),
            "attributes": {
                "friendly_name": friendly_name,
            }
        }
    
    logger.debug(f'posting to http://supervisor/core/api/states/{name}')
    
    response = requests.post(f'http://supervisor/core/api/states/{name}', headers=headers, json = entity)#, timeout=3)
    if( not response.ok):
        logger.error(f'failed to trigger {name} Error: {response.text}')

    logger.debug(response)
    return response.ok