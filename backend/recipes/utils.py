def convert_dict_to_text(dict):
    items = []
    for name, (amount, unit) in dict.items():
        items.append(f'{name} - {amount}{unit}')
    return ', '.join(items)
