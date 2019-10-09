class GetConfig:
    # COMMON
    DEFAULT_PAGE_TITLE = 'Unbabel Challenge'
    DEFAULT_COLUMN_SEPARATOR = ';'
    DEFAULT_ERROR_PREFIX = 'Translation-Error#'
    DEFAULT_PORT = 5500
    DEFAULT_URL = 'localhost'
    MAX_TEXT_LENGTH = 500

    # LANGUAGES
    DEFAULT_SOURCE_LANGUAGE = {'name': 'English', 'shortname':'en'}
    DEFAULT_TARGET_LANGUAGE = {'name': 'Spanish', 'shortname': 'es'}
    AVAILABLE_LANGUAGES = [{'name': 'Spanish', 'shortname': 'es'},
                           {'name': 'English', 'shortname': 'en'},
                           {'name': 'Portuguese', 'shortname': 'pt'},
                           {'name': 'French', 'shortname': 'fr'}
                           ]

    # STATUS
    TRANSLATED_STATUS = 'translated'
    REQUESTED_STATUS = 'requested'
    PENDING_STATUS = 'pending'

    # DATABASE
    DB_TRANSLATIONS_TABLE_NAME = 'translations'
    DB_NAME = 'unbabel_challenge'
    DB_USERNAME = 'postgres'
    DB_PW = 'root'
    DB_URL = 'localhost'
    DB_TYPE = 'postgresql'

    # API
    API_USERNAME = 'fullstack-challenge'
    API_KEY = '9db71b322d43a6ac0f681784ebdcc6409bb83359'
    API_GET_TRANSLATION_URL = 'https://sandbox.unbabel.com/tapi/v2/translation/'
    API_POST_TRANSLATION_URL = 'https://sandbox.unbabel.com/tapi/v2/translation/'

    # TESTING
    TEST_ORIGINAL_TEXT = 'Test'
    TEST_TRANSLATED_TEXT = ''
    TEST_UID = '1234'

    def __init__(self):
        pass