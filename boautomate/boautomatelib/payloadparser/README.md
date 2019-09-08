Payload Parser component
========================

*Executes on executive node*

Parses sent data in JSON format into one or multiple objects called **Facts**.
The **Facts** are statically typed objects, that should be required by tools used in your scripts.


### Example scenario of usage in a script

1. Your script needs a GIT tool
2. Boautomate looks at: Pipeline configuration and payload sent via POST
3. Boautomate constructs a tool basing on those information, so when you push to repository X, then GIT sends a webook in context of X, so a Fact in context of X is created
