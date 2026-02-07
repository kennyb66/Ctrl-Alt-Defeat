import json
import base64

# Load the human-readable JSON
with open("questions.json", "r") as f:
    data = f.read()

encoded = base64.b64encode(data.encode("utf-8")).decode("utf-8")

# Write the encoded file to game folder
with open("questions.dat", "w") as f:
    f.write(encoded)
