def item_by_source(source: str, data: dict | list):
    """Получение данных из объекта

    Args:
        source (str): путь, разделенный точками
        data (dict|list): даные

    Returns:
        Any: _description_

    Examples:
        >>> item_by_source('key1.0.key_deeper', {'key1': [{'key_deeper': 123}, 'other_key_deeper': 0], 'other_key': -1})
        123

        >>> item_by_source('0.key.1', [{'key': [0, -100, 2, 3]}, 123])
        -100
    """
    path = source.split(".")[0]

    try:
        data = data[int(path)]
    except (ValueError, TypeError):
        try:
            data = data[path]
        except TypeError:
            data = getattr(data, path)

    source_deeper = source.removeprefix(path).removeprefix(".")
    if not source_deeper:
        return data

    return item_by_source(source_deeper, data)
