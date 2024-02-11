# Documentation for errors.py

- [Documentation for errors.py](#documentation-for-errorspy)
  - [Functions](#functions)
    - [throw\_error](#throw_error)
    - [log](#log)
    - [Error codes](#error-codes)
  - [Example usage](#example-usage)
  - [Want me (Ornithopter747) to implement an error for you?](#want-me-ornithopter747-to-implement-an-error-for-you)


## Functions

### throw_error

```python
throw_error(error_code: ErrorCode, optional_text="default", optional_gui = True)
```

This function takes an ErrorCode enum as parameter
and throws the according error as a pop-up message. <br>
For example you can run `throw_error(ErrorCode.UNKNOWN)` <br>
There is an optional_text optional parameter that can be used for
optional text. <br>
There is also an optional_gui optional parameter that is True by
default but can be set to False, so no GUI is displayed

### log

```python
except Exception as e:
    log(e)
```

This function appends the exception to `ChaosCardGame/Debug/errorlog` for review.

### Error codes

```py
class ErrorCode(enum.Enum):
    [...]
```

The ErrorCode enum defines all possible error
codes. It is then used by `throw_error` to
know which error has to be thrown.

List of error codes:

```
UNKNOWN
TEST
CUSTOM
INVALID_ROOM_NAME
INVALID_USER_NAME
INVALID_IP
```

## Example usage

```py
import ChaosChardGame.Debug.errors as err

list = [1,2,3]

try:
    nonexistentelement = list[53]
except Exception as e:
    err.log(e)
    err.throw_error(err.ErrorCode.CUSTOM, optional_text=f"An error occured:\n{e}")
    # This is kinda dumb though cos the error will get logged twice
```

## Want me (Ornithopter747) to implement an error for you?

Create a github issue, tell me exactly where in your code and assign me to the issue.