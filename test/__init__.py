from generate_test_data import generate_test_data
import json
import io



def custom_format(data, indent = 1):
    spaces = ' ' * indent
    if isinstance(data, dict):
        formatted_items = [
            f'"{k}": {custom_format(v, indent + 4)}' for k, v in data.items()]
        formatted_str = '{\n' + ',\n'.join(
            spaces + item for item in formatted_items) + '\n' + spaces + '}'
    elif isinstance(data, list):
        formatted_items = ', '.join(custom_format(item) for item in data)
        formatted_str = '[' + formatted_items + ']'
    else:
        formatted_str = json.dumps(data)
    return formatted_str

print(custom_format(generate_test_data(25), 1))