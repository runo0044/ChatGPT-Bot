def DEFAULT_FIELD_STYLES():
    return {'asctime': {'color': 'green'},
            'levelname': {'color': 'blue', 'bold': True},
            'name': {'color': 'magenta'},
            'programname': {'color': 'cyan'}
            }


def DEFAULT_LEVEL_STYLES():
    return {
        'asctime': {'color': 'green'},
        'levelname': {'color': 'magenta', 'bold': True},
        'name': {'color': 'blue'},
        'programname': {'color': 'cyan'},
        'debug': {'color': 'blue', 'bold': True},
        'info': {'color': 'white', 'bold': True},
        'warning': {'color': 'yellow', 'bold': True},
        'error': {'color': 'red', 'bold': True},
        'critical': {'color': 'red', 'bold': True}
    }
