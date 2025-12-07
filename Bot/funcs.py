import json

def write(fp, data):
    with open(fp, "w") as file:
        json.dump(data, file, indent=2)


def read(fp):
    with open(fp) as file:
        data = json.load(file)
    return data