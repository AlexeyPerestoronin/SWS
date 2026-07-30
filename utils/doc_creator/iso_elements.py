def detect_iso_element(name):
    iso_element = ISO_ELEMENTS.get(name, None)
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


ISO_ELEMENTS = {
    'countersunk flat head cross recess': {
        'translation': 'винт с потайной головкой и крестообразным шлицем',
        'type_to_links': {}
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
