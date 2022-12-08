"""
A collection of utility modules.

These modules should not directly influence runtime behaviour
and should be as loosely coupled with the rest of the system as possible.

Internally, they should not:
    - Hardcode application specific values
    - Make requests
    - Interact with the file system
    - Use/change environment variables
    - Specify model schemas

Of course the APIs, they provide can be used to facilitate the above in
external modules.
"""