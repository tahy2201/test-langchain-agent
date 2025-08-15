
# hello_world_sdk.py

from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
import json

# Configure and Start the code interpreter session
code_client = CodeInterpreter('us-west-2')
code_client.start()

# Execute the hello world code
response = code_client.invoke("executeCode", {
    "language": "python", 
    "code": 'print("Hello World!!!")'
})

# Process and print the response
for event in response["stream"]:
    print(json.dumps(event["result"], indent=2))

# Clean up and stop the code interpreter sandbox session 
code_client.stop()
