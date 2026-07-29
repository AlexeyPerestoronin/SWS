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
        'type_to_links': {
            'ISO 7046-1 - M8 x 35 - Z - 35N':
            'https://www.ozon.ru/product/vint-m8-h-35-mm-potaynoy-30-sht-1804939507/?at=oZt6npq0Bh2XrnG6sQWXY83sN1zyrEU9nZ4lYI4yn4DE&sh=w7z-KQgUsg'
        }
    },
    'hex bolt': {
        'translation': 'болт шестигранный',
        'type_to_links': {
            'ISO 4014 - M10 x 70 x 26-N':
            'https://www.ozon.ru/product/bolt-m10-h-70-mm-1kg-shestigrannyy-otsinkovannyy-din-933-2545673143/?at=6WtZNlqLNu15DBpkU1XkqJ5TXg366wI5jLRwJh7N7w7W&sh=w7z-KazKlQ'
        }
    },
    'hex nut': {
        'translation': 'гайка шестигранная',
        'type_to_links': {
            'ISO - 4032 - M10 - W - N':
            'https://www.ozon.ru/product/gayka-shestigrannaya-m10-100sht-din-934-otsinkovannaya-2967340027/?at=mqtkxL9yxFZyE2j0cGp8j9OSNW3yz1hGGxBVpf2ko4Dj&sh=w7z-KazKlQ'
        }
    },
    'hex flange nut': {
        'translation': 'гайка шестигранная c фланцем',
        'type_to_links': {
            'ISO - 4161 - M8 - N':
            'https://www.ozon.ru/product/gayka-s-flantsem-m10-otsinkovannaya-10-sht-2558956778/?at=ywtA1mpO1FZmw4kjCR2x2WAC4r2Y9PSlDXzPMuDg51jx&sh=w7z-KazKlQ',
            'ISO - 4161 - M10 - N':
            'https://www.ozon.ru/product/gayka-s-flantsem-m10-otsinkovannaya-10-sht-2558956778/?at=ywtA1mpO1FZmw4kjCR2x2WAC4r2Y9PSlDXzPMuDg51jx&sh=w7z-KazKlQ'
        }
    }
}
