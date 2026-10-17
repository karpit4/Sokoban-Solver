def load_data_simple_alt(filename="data.json"):
    """
    Альтернативная версия - просто возвращает то, что прочитано из JSON
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    return data_list

simpledata = load_data_simple_alt('all_simple_levels.json')
harddata = load_data_simple_alt('hardlevels.json')

dataset = simpledata + harddata