LANGUAGE = 'ENG'

if LANGUAGE == 'ENG':
    from resources.libs.fcodes.fcodes.libs.data.kindships_ENG import consanguinity_key
elif LANGUAGE == 'ESP':
    from resources.libs.fcodes.fcodes.libs.data.kindships_ESP import consanguinity_key
else:
    raise ValueError('Language not supported')