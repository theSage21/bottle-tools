Bottle-Tools
============

A set of tools to make things easier to work with when using Bottle.
[Full Documentation](https://bottle-tools.readthedocs.io/en/latest/)


Autofill APIs with typed information

```python

import bottle_tools as bt

bt.common_kwargs.update({"User": UserTable})

@app.post('/calculate')
@bt.fill_args(coerce_types=True)
def login(usrname: str, pwd: str, User):
    user = User.get_or_404(usrname=usrname)
    if not user.password_is_correct(pwd):
        raise HttpNotFound()
    return 'ok'
```
