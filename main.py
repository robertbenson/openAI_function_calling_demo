import os

from dotenv import load_dotenv
from openai import OpenAI
import json


user_request = ("What are the icao codes within 20000 meters of John F "
                "Kennedy airport, Dublin and LAX , return long and "
                "lat in degrees for each and approximate distance in miles. All output is to be in json. The json fields to include are ICAO, name, city, lat, lon, distance_in_miles. The set shoud be called ICAOS")

load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")
model_version = "gpt-4o"

client = OpenAI()



def read_json(file_name: str):
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)
        json_string = json.dumps(data)
        return json_string


def get_icao(location, radius, unit, coordinates):
    """The model arguments have been passed to this function. At this point
    an api call would be made to retrieve the icao codes from an external
    source for that location. For this demo, the api call has been replaced
    with data read from 3 separate json files. One for each location."""

    icao_info = {
        "location": location,
        "radius": radius,
        "unit": unit,
        "coordinates": coordinates
    }

    # The api call would be here using a json string
    # The call has been replaced by 3 file reads.

    if ("John F Kennedy" in location):
        json_string = read_json('icao_usa_kjfk.json')
    elif ("LAX" in location):
        json_string = read_json('icao_usa_klax.json')
    elif ("Dublin" in location):
        json_string = read_json('icao_irl_eidw.json')
    else:
        json_string = json.dumps(icao_info)
    return json_string


def run_conversation(user_content: str):
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user",
                 "content": user_content}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_icao",
                "description": "Get the 4 digit ICAO code for a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "radius": {
                            "type": "integer",
                            "description": "distance from location in kilometers or miles",
                        },
                        "unit": {"type": "string",
                                 "description": "kilometers or miles",
                                 "enum": ["kilometers", "miles"]},
                        "coordinates": {"type": "string",
                                        "description": "longitude and latitude",
                                        "enum": ["minutes", "decimal"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=model_version,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response.choices[0].message.tool_calls

    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = {
            "get_icao": get_icao
        }

        messages.append(
            response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            print(f"\nModel Function Call: {tool_call.function.name}")
            print(f"Params:{tool_call.function.arguments}")
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(

                location=function_args.get("location"),
                radius=function_args.get("radius"),
                unit=function_args.get("unit"),
                coordinates=function_args.get("coordinates"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=model_version,
            messages=messages,
            response_format={"type": "json_object"},
            # stream=True
        )  # get a new response from the model where it can see the function
        return second_response

if __name__ == '__main__':
    print(f"\nRequest: {user_request}")
    response = run_conversation(user_request)
    print("")

    # The following code gives a scrolling effect. Data is being returned as it
    # is found, not necessarily all in one chunk.
    # stream=True

    # for chunk in response:
    #     print(chunk.choices[0].delta.content or "", end='', flush=True)

    json_string = response.choices[0].message.content
    print("JSON returned: ",json_string)

    data = json.loads(json_string)
    print(type(data))      # dictionary
    for icao in data['ICAOS']:
        print(icao)

    new_york_count = sum(1 for entry in data["ICAOS"] if entry["city"] == "New York")
    print("\n# New York entries returned: ", new_york_count)

    # Count the entries where first 2 characters of ICAO are "EI"
    ei_count = sum(
        1 for entry in data["ICAOS"] if entry["ICAO"].startswith("EI"))
    print("\n# Dublin entries returned: ", ei_count)
