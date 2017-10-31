# python-genderizeio

Simple Python wrapper for the [Genderize.io API](https://genderize.io).

Written to help manage rate-limiting, keep track of time window resets, and accommodate proxy use.

There's more about this written over at my blog:

[Determine the gender of a first name using Python](https://benjihughes.co.uk/blog/determine-the-gender-of-a-first-name-using-python/).

### Requirements
    
Requires the requests library for HTTP requests to the API.
	
    pip install requests
	

### Usage

Create a `Genderizeio` object then make use of the `genderize` function which returns a list of Python dictionaries representing the JSON response from the API.


### Handling rate limiting

The `Genderizeio` object provides properties that are updated after each request to allow rate limiting to be monitored.

```python
from Genderizeio import Genderizeio

gen = Genderizeio()
gen.genderize(['Emily']) 

# Total requests allowed in time window
print gen.rate_limit
>>> 1000

# Remaining requests within time window
print gen.rate_limit_remaining
>>> 999

# Time until rate limit window resets (stays up to date until it reaches 0)
print gen.time_until_reset  
>>> 600

time.sleep(30)  # Doesn't require another request to update

print gen.time_until_reset  
>>> 570

```


## Examples


### Example Query
```python
from Genderizeio import Genderizeio

proxies = {'http':'127.0.0.1:80'}
gen = Genderizeio(proxies=proxies) # Optional proxy support

print gen.genderize(['Emily', 'Jack']) 
```


### Example response
```json
[{
  "name": "emily",
  "gender": "female",
  "probability": 1,
  "count": 3765
},
{
  "name": "jack",
  "gender": "male",
  "probability": 0.99,
  "count": 1993
}]
```

	
### Full usage example

  ```python
from Genderizeio import Genderizeio

proxies = {'http':'127.0.0.1:80'}

gen = Genderizeio(proxies=proxies)  # Create object

results = gen.genderize(['Emily', 'Jack'])  # Genderize name(s) (String or List)

# View results
for res in results:
    print '{prob}% probability that {name} is a {gender} name.'.format(
        name=res['name'],
        gender=res['gender'],
        prob=int(res['probability']*100))

# View rate limits
print "{remain}/{limit} requests remaining".format(
    remain=gen.rate_limit_remaining,
    limit=gen.rate_limit)
    
# View live reset counter
print "{window} seconds until rate limit window resets".format(
    window=gen.time_until_reset)

>>> 100% probability that Emily is a female name.
      99% probability that Jack is a male name.
      955/1000 requests remaining
      82199 seconds until rate limit window resets
```
