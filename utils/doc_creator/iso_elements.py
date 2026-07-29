def detect_iso_element(name):
    iso_element = iso_elements_data_table.get(name, None)
    if not iso_element:
        raise Exception(f"cannot detect ISO element '{name}'")
    return iso_element


def detect_translation(name: str) -> str:
    translation = detect_iso_element(name).get('translation', None)
    if not translation:
        raise Exception(f"cannot detect translation for ISO element '{name}'")
    return translation


def detect_link(name: str, type: str) -> str:
    return detect_iso_element(name)['type_to_links'].get(type, 'отсутствует')


iso_elements_data_table = {
    'countersunk flat head cross recess': {
        'translation': 'винт с потайной головкой и крестообразным шлицем',
        'type_to_links': {
            'ISO 7046-1 - M8 x 35 - Z - 35N':
            'https://www.ozon.ru/product/vint-m8-h-35-mm-potaynoy-30-sht-1804939507/?at=oZt6npq0Bh2XrnG6sQWXY83sN1zyrEU9nZ4lYI4yn4DE&sh=w7z-KQgUsg'
        }
    },
    'hex bolt': {
        'translation': 'болт шестигранный',
        'type_to_links': {}
    },
    'hex nut': {
        'translation': 'гайка шестигранная',
        'type_to_links': {}
    },
    'hex flange nut': {
        'translation': 'гайка шестигранная c фланцем',
        'type_to_links': {}
    }
}
