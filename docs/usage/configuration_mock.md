# ⚙️ Configuration mocks.json

## General file structure
### Location of all mockups
```json
[
  #All mocks must be between square brackets.
]
```
---
### mocks.json is a JSON array, each element is an object describing a single mock endpoint. Example of a single element:
```json
{
  "path": "/abc/xyz/",
  "method": "POST" or ["GET", "POST", ...],
  "data": [ ... ],
  "response": { ... },
  "status": 200,
  "on_pass": {"response": {...}, "status": 200},
  "on_fail": {"response": {...}, "status": 422},
  "delay": 10,
  "generate_response": {
    "locale": "en_US",
    "count": 10,
    "response": {...}
  },
  "shuffle": true,
  "unstable": {
    "fail_rate": 0.5,
    "status": 503,
    "response": {...}
  },
  "fallback_data": false
}
```
---
### Entry fields
1. ```path``` (string, required)
Request path, for example **"/api/product/get/"**.
2. ```method``` (string|array of strings, required)
**GET**, **POST**, etc.
3. ```data``` (array of rule objects, optional)
A list of input validation rules. Each element is an object.
**{ name, type?, if? }**
4. ```response``` (object|array|any, optional)
Static response body.
5. ```status``` (int, optional)
The HTTP status corresponding to **response**.
If left blank it will be 200.
6. ```on_pass / on_fail``` (object, optional)
If **data** is specified, then **on_pass** is returned upon validation, and **on_fail** is returned upon error.
Format: **{"response": ..., "status": 200}**
7. ```delay``` (float|array of float, optional) delay in **seconds**
8. ```generate_response``` (dict, optional)
9. ```shuffle``` (boolean, optional)
10. ```unstable``` (object, optional) - unstable behavior settings (see the "Unstable behavior" section).
11. ```fallback_data``` (boolean, optional) - return data if there is no response
---
### Precision for float values
#### If you're generating a ```float``` value using a range (e.g., ```[min, max]```), you can specify **a third number** to control the number of digits after the decimal point.
**Example**:
```json
{"type": "float", "value": [0.5, 5.5, 2] }
```
---
## Types
### Supported values ​​for the type field (case insensitive):
- ```int``` - integers
- ```float``` - floating-point number (float, int) (integers are treated as floats)
- ```str``` - string
- ```bool``` - boolean value
- ```list``` - array
- ```dict``` - dictionary
- ```any``` - any type
### Feature: bool is not treated as int.
---
## Conditions - ```if``` field syntax
### The ```if``` field can be a string or an object **{op, value}**. Supported constructs (string syntax):
1. Comparisons: ```> 10```, ```>= 0```, ```< 5```, ```== "x"```, ```!= 0```.
2. ```between low high``` - checks ```low <= float(val) <= high```.
3. ```regex:...``` - uses ```re.search``` (the string must match a pattern somewhere inside). For fullmatch, use ```^...$```.
4. ```in [a, b, c]``` / ```not_in [a, b]``` - membership.
5. ```min_length N``` ```/ max_length N``` - checking length.
#### Alternatively, you can use the dictionary form: ```{ "op": ">", "value": 10 }```.
---
## Dynamic response generation
If the mock endpoint object specifies a ```generate_response``` block, the returned response will be generated dynamically, rather than taken from the ```response``` field.
### Structure of the ```generate_response``` field
```json
"generate_response": {
  "locale": "en_US",        // Language/region for data generation via Faker
  "count": 10,              // Number of elements. You can specify a number or a range [min, max]
  "response": {             // Generated object template
    "name": "name",
    "email": "email",
    "created": "date_time"
  }
}
```
#### Alternatively, you can pass an array of templates:
```json
"generate_response": {
  "locale": "en_US",
  "count": [5, 15],
  "response": [
    { "type": "word", "value": "text" },
    { "type": "uuid4", "value": "another" }
  ]
}
```
---
### Supported values ​​in the template
The template is a dictionary (```dict```), where the keys are the field names and the values ​​are either:
- Function name from the **Faker** library, for example:
  - ```"name"```, ```"email"```, ```"uuid4"```, ```"address"```, ```"company"```, ```"date_time"```, ```"word"```, etc.
- Number range: ```[min, max]``` — will generate a random integer.
- Any other value will be used as is.
- Values ​​like ```"somevalue.unGen"``` will be replaced with ```"somevalue"``` (used to disable generation for a specific field).
### How does ```generate_response``` work?
- If ```count``` is a number, exactly that many objects will be generated.
- If ```count``` is a list of two numbers ```[min, max]```, the count is chosen randomly within that range.
- If ```response``` is a single template, it is reused.
- If ```response``` is an array of templates, they are chosen randomly for each entry.
---
## Shuffle Behavior
#### If ```shuffle: true``` and the result is an array, it will be shuffled before being returned.
---
## Unstable behaviour (```unstable```)
The ```unstable``` option allows you to simulate intermittent errors:
```json
"unstable": {
  "fail_rate": 0.5,
  "status": 503,
  "response": {"error": "service unavailable"}
}
```
* ```fail_rate``` (**float**) - the chance (0..1) that the request will return an error from ```unstable```. For example, 0.1 = 10%.
* ```status``` (**integer**) - HTTP status in case of error.
* ```response``` (**any**) - the body of the response in case of an error.
---
## JSON Schema-like notation
```
mocks: array[
  {
    path: string,
    method: string|array of strings,
    data?: array[
      {name: string, type?: string, if?: string | {op: string, value: any}}
    ],
    response?: any,
    status?: integer,
    on_pass?: {response : any, status: integer},
    on_fail?: {response: any, status: integer},
    delay?: float|[float, float, integer],
    generate_response?: dict{
      locale: string,
      count: integer|[integer, integer],
      response: dict
    },
    shuffle?: boolean,
    unstable?: {
      fail_rate: float, 
      status: integer, 
      response: any
    },
    fallback_data?: boolean
  }
]
```
## See [examples](examples_mocks.md) to understand better.