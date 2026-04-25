import utils.console as console

def validate_input(prompt, mapping):
    value = mapping.get(input(prompt))
    if not value:
        return None
    return value