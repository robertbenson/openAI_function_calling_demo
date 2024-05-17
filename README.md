# OpenAI - Function Calling Demo - using Python

### Objective 

"What are the icao codes within 20000 meters of John F Kennedy airport, Dublin and LAX , return long and lat in degrees for each and approximate distance in miles ?".

_An ICAO is a 4 digit alphanumeric that uniquely identifies an airport/airfield. e.g. EINN is the ICAO for Shannon Airport, Ireland._

# [Function Calling](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models) - with model generated arguments

## Step 1: send the conversation and available functions to the model
OpenAI will identify the arguments required from the request
## Step 2 :check if the model wanted to call a function
For this demo, the model did want to call a function, 3 times, once for each location.
Note how the model was able to determine the model arguments from the request.

### 1st time function call:

`Function: get_icao `

`Params:{"location": "John F Kennedy airport", "radius": 20, "unit": "miles", "coordinates": "decimal"}`

### 2nd time function call:
`
Function: get_icao`

`
Params:{"location": "Dublin", "radius": 20, "unit": "miles", "coordinates": "decimal"}
`
### 3rd time function call:
`
Function: get_icao
`

`
Params:{"location": "LAX", "radius": 20, "unit": "miles", "coordinates": "decimal"}
`
# Step 3: call the function
# Step 4: send the info for each function call and function response to the model


    OpenAI will augment the data supplied by the user function call with OpenAI modifications
    The data supplied by the user did not contain a distance. OpenAI augmented that information on the second pass of the model.

20,000 meters is an unusual amount. Why not just say 20 km ? OpenAI can handle this and do the conversion.
20km is around 12.4 miles.
One api call will not facilitate a final solution for this use case. 3 separate api calls will be required to facilitate a final solution, one call for each airfield.

For the purpose of this demo, the data is supplied in json format from 3 separate file, one file representing each location.


## Create an OpenAI account

[OpenAI Quickstart](https://platform.openai.com/docs/quickstart)


set up an OPENAI API KEY
### Model

This python script will use model_version = `gpt-4o`

OpenAI has different model offerings and price points. [models and price points](https://platform.openai.com/docs/models)
                                                                                 
## Install packages to run the demo


Manage environment variables, sensitive information. Hide the api key from public view for security
```python
pip install python_dotenv  
```
Install or upgrade the OpenAI Python package
```python
pip install --upgrade openai
```

### Python Code 
[sample OpenAI function calling example](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models)


The supplied openai code has been modified to:
1. use dotenv to hide the api key
2. modify the content for my use case: `"What are the icao codes within 20000 meters of John F Kennedy airport, Dublin and LAX , return long and lat in degrees for each and approximate distance in miles ?".`


#### Python Code - build json for api call using model generated arguments 
```python
def get_icao(location, radius, unit, coordinates):
    """Build Json for call to api"""

    icao_info = {
        "location": location,
        "radius": radius,
        "unit": unit,
        "coordinates": coordinates
    }
    # The actual code has 3 calls to json files to simulate the passing of data.
    json_string = json.dumps(icao_info)
    print(
        f"Run your api here with the parameters extracted from the request: {json_string}\n")
    return json_string
```




### Model Generated Arguments
The parameters that are required for our use case are detailed with a type and description. A detailed and specific description is required in order to inform openai had to handle the response.
For our custom api, we will require: location, radius, unit and coordinates. 
1. Location 
```
location: {"type": "string","description": "The city and state, e.g. San Francisco, CA",},
```
2. radius
```
radius: {"type": "integer", "description": "distance from location in kilometers or miles"},
```
3. unit - kilometers or miles

Inform OpenAI that kilometers or miles are required as a model argument using an enumerator.

```
unit: {"type": "string","description": "kilometers or miles","enum": ["kilometers", "miles"]},
```
4. coordinates - in minutes or decimal

The request did not specifically ask for longitude and latitude, it asked for long and lat, however OpenAI was able to work out by context
that longitude and latitude were required.
Inform OpenAI that a model argument of either minutes or decimal is required, using an enumerator.
```
coordinates: {"type": "string","description": "longitude and latitude", "enum": ["minutes", "decimal"]},
```

#### Python Code - define the model generated arguments


```python
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
    

```


## OpenAI Generated Output 
### Response from the chat request:
```
Request: What are the icao codes within 20000 meters of John F Kennedy airport, Dublin and LAX , return long and lat in degrees for each and approximate distance in miles ?

Model Function Call: get_icao
Params:{"location": "John F Kennedy Airport, NY", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}

Model Function Call: get_icao
Params:{"location": "Dublin, Ireland", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}

Model Function Call: get_icao
Params:{"location": "LAX, CA", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}

### Airports within 20,000 meters of John F. Kennedy Airport (JFK)
1. **John F Kennedy Intl (KJFK)**
   - Latitude: 40.63975
   - Longitude: -73.77892
   - Distance: 0 miles

2. **Idlewild Intl (KIDL)**
   - Latitude: 40.63975
   - Longitude: -73.77892
   - Distance: 0 miles

3. **La Guardia (KLGA)**
   - Latitude: 40.777245
   - Longitude: -73.872604
   - Distance: ~10 miles

4. **East 34th Street Heliport (TSS)**
   - Latitude: 40.7425
   - Longitude: -73.97195
   - Distance: ~12 miles

5. **One Police Plaza Heliport (NK39)**
   - Latitude: 40.7126
   - Longitude: -73.9996
   - Distance: ~13 miles

6. **Wall Street Heliport (KJRB)**
   - Latitude: 40.701214
   - Longitude: -74.009026
   - Distance: ~14 miles

7. **West 30th St. Heliport (KJRA)**
   - Latitude: 40.7545
   - Longitude: -74.0071
   - Distance: ~15 miles

### Airports within 20,000 meters of Dublin Airport (EIDW)
1. **Dublin (EIDW)**
   - Latitude: 53.421333
   - Longitude: -6.270075
   - Distance: 0 miles

2. **Weston Airport (EIWT)**
   - Latitude: 53.351334
   - Longitude: -6.4875
   - Distance: ~10 miles

3. **Casement (EIME)**
   - Latitude: 53.301666
   - Longitude: -6.451333
   - Distance: ~13 miles

### Airports within 20,000 meters of Los Angeles International Airport (LAX)
1. **Los Angeles Intl (KLAX)**
   - Latitude: 33.942535
   - Longitude: -118.40807
   - Distance: 0 miles

2. **Jack Northrop Fld Hawthorne Muni (KHHR)**
   - Latitude: 33.92284
   - Longitude: -118.33518
   - Distance: ~5 miles

3. **Santa Monica Municipal Airport (KSMO)**
   - Latitude: 34.015835
   - Longitude: -118.45131
   - Distance: ~9 miles

4. **Zamperini Field Airport (KTOA)**
   - Latitude: 33.80339
   - Longitude: -118.33961
   - Distance: ~14 miles
```
### JSON output

#### [JSON Mode](https://platform.openai.com/docs/guides/text-generation/json-mode)
set the response format
```Python
second_response = client.chat.completions.create(
            model=model_version,
            messages=messages,
            response_format={"type": "json_object"},       <<<<<<<<<<<<<<<<<<<<<<<<<<
            # stream=True
        ) 
         
```



`user_request = ("What are the icao codes within 20000 meters of John F "
                "Kennedy airport, Dublin and LAX , return long and "
                "lat in degrees for each and approximate distance in miles. All output is to be in json. The json fields to include are ICAO, name, city, lat, lon, distance_in_miles.")`

```JSON
JSON returned:  

{
  "results": [
    {
      "location": "John F Kennedy Airport, NY",
      "icao_codes": [
        {
          "ICAO": "KJFK",
          "name": "John F Kennedy Intl",
          "city": "New York",
          "lat": 40.63975,
          "lon": -73.77892,
          "distance_in_miles": 0
        },
        {
          "ICAO": "KIDL",
          "name": "Idlewild Intl",
          "city": "New York",
          "lat": 40.63975,
          "lon": -73.77892,
          "distance_in_miles": 0
        },
        {
          "ICAO": "KLGA",
          "name": "La Guardia",
          "city": "New York",
          "lat": 40.777245,
          "lon": -73.872604,
          "distance_in_miles": 8.91
        },
        {
          "ICAO": "NK39",
          "name": "One Police Plaza Heliport",
          "city": "New York",
          "lat": 40.7126,
          "lon": -73.9996,
          "distance_in_miles": 17.04
        },
        {
          "ICAO": "KJRB",
          "name": "Wall Street Heliport",
          "city": "New York",
          "lat": 40.701214,
          "lon": -74.009026,
          "distance_in_miles": 17.71
        }
      ]
    },
    {
      "location": "Dublin",
      "icao_codes": [
        {
          "ICAO": "EIDW",
          "name": "Dublin",
          "city": "Dublin",
          "lat": 53.421333,
          "lon": -6.270075,
          "distance_in_miles": 0
        },
        {
          "ICAO": "EIWT",
          "name": "Weston Airport",
          "city": "Leixlip",
          "lat": 53.351334,
          "lon": -6.4875,
          "distance_in_miles": 13.19
        },
        {
          "ICAO": "EIME",
          "name": "Casement",
          "city": "Casement",
          "lat": 53.301666,
          "lon": -6.451333,
          "distance_in_miles": 15.5
        }
      ]
    },
    {
      "location": "LAX",
      "icao_codes": [
        {
          "ICAO": "KLAX",
          "name": "Los Angeles Intl",
          "city": "Los Angeles",
          "lat": 33.942535,
          "lon": -118.40807,
          "distance_in_miles": 0
        },
        {
          "ICAO": "KHHR",
          "name": "Jack Northrop Fld Hawthorne Muni",
          "city": "Hawthorne",
          "lat": 33.92284,
          "lon": -118.33518,
          "distance_in_miles": 4.68
        },
        {
          "ICAO": "KSMO",
          "name": "Santa Monica Municipal Airport",
          "city": "Santa Monica",
          "lat": 34.015835,
          "lon": -118.45131,
          "distance_in_miles": 7.23
        },
        {
          "ICAO": "KTOA",
          "name": "Zamperini Field Airport",
          "city": "Torrance",
          "lat": 33.80339,
          "lon": -118.33961,
          "distance_in_miles": 13.64
        }
      ]
    }
  ]
}
```
### Custom JSON using supplied model arguments

3 JSON builds were generated using model arguments

The model has identified arguments from the request:
The 3 locations are populated with the airfield names.

The radius is 20 , unit is kilometers (20,000 meters) and coordinates as minutes.

```JSON 
{"location": "John F Kennedy Airport, NY", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}
{"location": "Dublin, Ireland", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}
{"location": "LAX, CA", "radius": 20, "unit": "kilometers", "coordinates": "decimal"}
```
These can be used in 3 separate api calls as required.
## Key Take Away

### One Request

"What are the icao codes within 20000 meters of John F Kennedy airport, Dublin and LAX , return long and lat in degrees for each and approximate distance in miles ?".
### Iterative - 3 responses



OpenAI has extracted the model arguments from the request. It has identified that 3 airfields are required and supplied information to make 3 separate api calls. 
### Conversion - context and inference

The requested distance was 20,000 meters. However, OpenAI has noted that acceptable responses are miles or kilometers and has automatically converted the parameters, radius and units to 20 and kilometers respectively.

### OpenAI Model has augmented the response

The model has determined the model arguments from the user request, (first time to access the model). The data has been retrieved and added to the model.
The model had been accessed for a second time to refine the answer.

OpenAI did not accept at face value the data supplied by the user was correct. Airfield data was added that was outside the 20km range, but OpenAI correctly identified these airfields, in step 4, and did not report on them.