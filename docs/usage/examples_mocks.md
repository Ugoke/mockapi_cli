## Examples
### 1. Static GET - Server Status
```json
{
  "path": "/api/status/",
  "method": "GET",
  "response": {"status": "ok", "version": "1.0.0"},
  "status": 200,
  "data": []
}
```
Explanation: simple static response, no validation.
***
### 2. POST JSON - user creation (name, email, avatar file)
```json
{
  "path": "/api/user/create/",
  "method": "POST",
  "data": [
    {"name": "user.name", "type": "str", "if": "min_length 3"},
    {"name": "user.email", "type": "str", "if": "regex:^\\S+@\\S+\\.\\S+$"},
    {"name": "avatar", "type": "any"}
  ],
  "on_pass": {"response": {"created": true}, "status": 201},
  "on_fail": {"response": {"created": false, "errors": []}, "status": 400}
}
```
Example of ```Content-Type: application/json body``` that will pass:
```json
{
  "user": {"name": "User", "email": "user@example.com"},
  "avatar": null
}
```
An example that won't work:
```json
{
    "user": {"name": 1, "email": "bad-email"}
}
```
***
### 3. POST - order with checking of the first position (if you check only index 0)
```json
{
  "path": "/api/order/create/",
  "method": "POST",
  "data": [
    {"name": "customer.email", "type": "str", "if": "regex:^\\S+@\\S+\\.\\S+$"},
    {"name": "items", "type": "list"},
    {"name": "items.0.product_id", "type": "int", "if": ">0"},
    {"name": "items.0.quantity", "type": "int", "if": ">=1"},
    {"name": "items.0.price", "type": "float", "if": ">=0"}
  ],
  "on_pass": {"response": {"order_created": true}, "status": 200},
  "on_fail": {"response": {"order_created": false, "errors": []}, "status": 422}
}
```
Explanation: ```items``` is validated as a list + only the first element ```items[0]```. To cover all elements, see example 5.
Example of a body, will pass:
```json
{
  "customer": {"email": "user@shop.com"},
  "items": [{"product_id": 12, "quantity": 2, "price": 9.99}]
}
```
***
### 4. POST - search with filters (```in``` and ```page```)
```json
{
  "path": "/api/search/",
  "method": "POST",
  "data": [
    {"name": "query", "type": "str", "if": "min_length 1"},
    {"name": "filters.category", "type": "str", "if": "in [\"electronics\", \"books\", \"clothing\"]"},
    {"name": "page", "type": "int", "if": ">=1"}
  ],
  "on_pass": {"response": {"results": [], "ok": true}, "status": 200},
  "on_fail": {"response": {"ok": false, "errors": []}, "status": 400}
}
```
Example of a body, will pass:
```json
{
  "query": "headphones",
  "filters": {"category": "electronics"},
  "page": 1
}
```
***
### 5. Validation of all order elements - option (workaround)
```json
{
  "path": "/api/order/items/bulk/",
  "method": "POST",
  "data": [
    {"name": "product_id", "type": "int", "if": ">0"},
    {"name": "quantity", "type": "int", "if": ">=1"},
    {"name": "price", "type": "float", "if": ">=0"}
  ],
  "on_pass": {"response": {"ok": true}, "status": 200},
  "on_fail": {"response": {"ok": false, "errors": []}, "status": 422}
}
```
Requirement: The request body is an array of elements, for example:
```json
[
  {"product_id": 1, "quantity": 2, "price": 5.0},
  {"product_id": 2, "quantity": 1, "price": 12.5}
]
```
***
### 6. Example with between and float/int
```json
{
  "path": "/api/product/get/",
  "method": "POST",
  "data": [
    {"name": "user.id", "type": "int", "if": ">0"},
    {"name": "items.0.price", "type": "float", "if": "between 10 100"}
  ],
  "on_pass": {"response": {"ok": true}, "status": 200},
  "on_fail": {"response": {"ok": false, "errors": []}, "status": 422}
}
```
Examples:
- ```items.0.price = 50``` → will pass (```int``` is considered acceptable for ```float```).
- ```items.0.price = 5``` → will not work (```5 is not between 10 and 100```).
***
### 7. Example of a condition in dict form (option instead of string)
```json
{
  "path": "/api/example/threshold/",
  "method": "POST",
  "data": [
    {"name": "value", "type": "int", "if": {"op": ">", "value": 100}}
  ],
  "on_pass": {"response": {"ok": true}, "status": 200},
  "on_fail": {"response": {"ok": false, "errors": []}, "status": 422}
}
```
Explanation: ```if``` can be specified as ```{"op": "...", "value": ...}``` - convenient when generating a configuration.
***
### 8. Example of ```not_in``` and ```max_length```
```json
{
  "path": "/api/comment/create/",
  "method": "POST",
  "data": [
    {"name": "author", "type": "str", "if": "max_length 50"},
    {"name": "text", "type": "str", "if": "min_length 1"},
    {"name": "status", "type": "str", "if": "not_in [\"spam\", \"banned\"]"}
  ],
  "on_pass": {"response": {"created": true}, "status": 201},
  "on_fail": {"response": {"created": false, "errors": []}, "status": 400}
}
```
***
### 9. Example with several ```methods```
```json
{
  "path": "/api/product/get_or_post/",
  "method": ["POST", "GET"],
  "data": [
    {"name": "id", "type": "int", "if": ">0"}
  ],
  "on_pass": {"response": {"ok": true}, "status": 200},
  "on_fail": {"response": {"ok": false, "errors": "validation failed"}, "status": 422},
  "response": {"id": 10}
}
```
Explanation:
- POST request
  - The input data described in ```data``` is checked.
  - If the data passes validation, ```on_pass``` is returned.
  - If the data does not pass validation, ```on_fail``` is returned.
- GET request:
  - Validation is **not performed**.
  - The contents of the ```response``` field are returned immediately.
***
### 10. Example with a delay
```json
{
  "path": "/api/product/delay_10/",
  "delay": 10,
  "method": "GET",
  "response": {"delay": 10}
}
```
Explanation: In this example the ```delay``` is **10 seconds**
You can also specify a random range
```json
{
  "path": "/api/product/delay_3_4/",
  "delay": [3, 4],
  "method": "GET",
  "response": {"delay": 34}
}
```
***
### 11. Example with generation
```json
{
  "path": "/api/products/",
  "method": "GET",
  "generate_response": {
    "locale": "en_US",
    "count": [5, 10],
    "response": {
      "id": "uuid4",
      "name": "word",
      "price": [100, 500],
      "available": "boolean",
      "created": "date_time"
    }
  }
}
```
Explanation:
- Generates ```5 to 10``` response objects.
- Uses **Faker** with ```en_US``` locale.
- Each field is filled in according to the template:
  - ```"uuid4"``` → random UUID.
  - ```"word"``` → random word.
  - ```[100, 500]``` → random number from range.
  - ```"boolean"``` → random true/false value.
  - ```"date_time"``` → random date and time.
***
### 12. Example with shuffle
```json
{
  "path": "/api/product/shuffle/",
  "method": "GET",
  "shuffle": true,
  "response": [
    {"id": 1, "price": 12.5, "title": "USB cable"},
    {"id": 2, "price": 99.9, "title": "Wireless headphones"}
  ],
  "status": 200
}
```
Explanation: When ```shuffle: true``` is specified, the response list is shuffled.
***
## Example with unstable behaviour
```json
{
  "path": "/api/product/fail_rate/50/",
  "method": "GET",
  "response": [
    {"id": 1, "price": 12.5, "title": "USB cable"}
  ],
  "unstable": {
    "fail_rate": 0.5,
    "status": 503,
    "response": {"error": "Service Unavailable"}
  },
  "status": 200
}
```
Explanation: Will return an error with a **50%** chance
***