import logging


def substitute_parameters(sentence: str, parameters: dict) -> str:

    # match = re.search("(\#\w+\.\w+)|(\$\w+)", sentence)
    # params = [x for x in match.groups() if x is not None] if match else []

    for key in parameters:
        value = parameters[key]

        # if key == 'person_name':
        # value = value['name']

        patterns = [f"#globals.{key}", f"${key}"]

        for pattern in patterns:
            # for param in params:
            # if pattern == param:
            try:
                # if value is not string then try original
                if type(value) != str:
                    value = parameters.get(f"{key}.original", "")
                    # checking if original is string
                    if type(value) != str:
                        # if repeated field then take the first value
                        if len(value) > 0:
                            value = value[0]

                if type(value) == str and value != "":
                    sentence = sentence.replace(pattern, value)
            except Exception as e:
                logging.exception(e)
    return sentence
