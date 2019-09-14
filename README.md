Bottle-Tools
============

A set of tools to make things easier to work with when using Bottle.
[Full Documentation](https://bottle-tools.readthedocs.io/en/latest/)


Autofill APIs with typed information

```
@app.post('/calculate')
@fill_args(coerce_types=True)
def fancy_calculation(a: int, b: float):
    return {'result': a + b}
```
