import os

from dotenv import load_dotenv
from openai import OpenAI
import json

user_request = (
    "What are the airports (icao codes) within 20000 meters of John F "
    "Kennedy airport, Dublin and LAX , return long and "
    "lat in degrees for each and approximate distance in miles. All output "
    "is to be in json. The json fields to include are ICAO, name, city, lat, "
    "lon, distance_in_miles and TZ. The set should be called ICAOS")

load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")
model_version = "gpt-4o"

client = OpenAI()


def read_json(file_name: str):
    with open(file_name, 'r') as json_file:
        data1 = json.load(json_file)
        json_file_string: str = json.dumps(data1)
        return json_file_string


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

    if "John F Kennedy" in location:
        json_str = read_json('icao_usa_kjfk.json')
    elif "LAX" in location:
        json_str = read_json('icao_usa_klax.json')
    elif "Dublin" in location:
        json_str = read_json('icao_irl_eidw.json')
    else:
        json_str = json.dumps(icao_info)
    return json_str


def run_conversation(user_content: str, seed=None):
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
                            "description": "The city and state, e.g. San "
                                           "Francisco, CA",
                        },
                        "radius": {
                            "type": "integer",
                            "description": "distance from location in "
                                           "kilometers or miles",
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
    # tool_calls = response.choices[0].message.tool_calls

    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = {
            "get_icao": get_icao
        }

        messages.append(
            response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response
        # to the model
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
            seed=seed,
            temperature=0,
            # stream=True
        )  # get a new response from the model where it can see the function
        return second_response


def process_output(json_str: str):
    data = json.loads(json_str)
    print(type(data))  # dictionary
    print("data:", data)

    save_model_data(data)

    for icao in data['ICAOS']:
        print(icao)

    count = len(data["ICAOS"])
    new_york_count = sum(
        1 for entry in data["ICAOS"] if entry["city"] == "New York")

    # Count the entries where first 2 characters of ICAO are "EI"
    ei_count = sum(
        1 for entry in data["ICAOS"] if entry["ICAO"].startswith("EI"))

    Los_Angeles_count = sum(
        1 for entry in data["ICAOS"] if entry["TZ"].endswith("Los_Angeles"))

    print("")
    print("{:<30}{:>5}".format("The count of all ICAO\'s is:", count))
    print("{:<30}{:>5}".format("New York entries returned:", new_york_count))
    print("{:<30}{:>5}".format("Dublin entries returned:", ei_count))
    print("{:<30}{:>5}".format("Los Angeles entries returned:",
                               Los_Angeles_count))


def save_model_data(data):
    with open('data_from_openai.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    print(f"\nRequest: {user_request}")
    response = run_conversation(user_request, 123)
    print("")

    # The following code gives a scrolling effect. Data is being returned as it
    # is found, not necessarily all in one chunk.
    # stream=True

    # for chunk in response:
    #     print(chunk.choices[0].delta.content or "", end='', flush=True)

    json_string = response.choices[0].message.content
    print("JSON returned: ", json_string)

    process_output(json_string)
