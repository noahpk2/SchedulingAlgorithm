import json


def parse_json_data(json_string):
    """Parse a JSON string and return a predefined structure."""
    # Decode the JSON string into a dictionary
    parsed_data = json.loads(json_string)

    # Enforce the structure on the parsed data
    structured_data = enforce_structure(parsed_data)

    return structured_data


def enforce_structure(data):
    """Enforce a predefined structure on the parsed data."""

    # 1. Enforce structure for 'hours'
    if 'hours' not in data or not isinstance(data['hours'], dict):
        raise ValueError("Missing or incorrect type for key: hours")
    for day, timing in data['hours'].items():
        if 'operatingHours' not in timing or not isinstance(timing['operatingHours'], list):
            raise ValueError(
                f"Missing or incorrect type for operatingHours for day: {day}")

    # 2. Enforce structure for 'dailyTraffic'
    if 'dailyTraffic' not in data or not isinstance(data['dailyTraffic'], dict):
        raise ValueError("Missing or incorrect type for key: dailyTraffic")
    for day, traffic in data['dailyTraffic'].items():
        if not all(isinstance(i, int) for i in traffic):
            raise ValueError(
                f"Incorrect values in dailyTraffic for day: {day}")

    # 3. Enforce structure for 'positions'
    if 'positions' not in data or not isinstance(data['positions'], dict):
        raise ValueError("Missing or incorrect type for key: positions")
    for position, details in data['positions'].items():
        if 'maxGuests' not in details or not isinstance(details['maxGuests'], int):
            raise ValueError(
                f"Missing or incorrect type for maxGuests in position: {position}")
        if 'rate' not in details or not isinstance(details['rate'], int):
            raise ValueError(
                f"Missing or incorrect type for rate in position: {position}")

    # 4. Enforce structure for 'empl'
    if 'empl' not in data or not isinstance(data['empl'], list):
        raise ValueError("Missing or incorrect type for key: empl")
    for employee in data['empl']:
        if 'id' not in employee or not isinstance(employee['id'], int):
            raise ValueError(
                "Missing or incorrect type for id in employee data")
        if 'pos' not in employee or not isinstance(employee['pos'], str):
            raise ValueError(
                "Missing or incorrect type for pos in employee data")
        if 'ph' not in employee or not isinstance(employee['ph'], int):
            raise ValueError(
                "Missing or incorrect type for ph in employee data")
        if 'avl' not in employee or not isinstance(employee['avl'], list):
            raise ValueError(
                "Missing or incorrect type for avl in employee data")

    return data






# Add the updated functions to our script content




