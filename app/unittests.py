"""
To execute a particular class of tests, run the following command:
py -m unittest unittests.*CLASSNAME*

To execute a test on all classes, run the following command:
py unittests.py
"""
from database import engine
import unittest
import routes
import config
import models


class TestAPI(unittest.TestCase):
    """
    Class to perform API tests, such as requests to a translation, get a translation update and input text verifications.
    """
    @classmethod
    def setUpClass(self):
        self.translation_api = routes.api_request_translation(config.GetConfig.TEST_ORIGINAL_TEXT)
        self.translation_api_get = routes.api_get_translation(self.translation_api['uid'])

    def test_api_request(self):
        self.assertNotIn(str(self.translation_api), config.GetConfig.DEFAULT_ERROR_PREFIX)
        self.assertEqual(self.translation_api['source_language'],config.GetConfig.DEFAULT_SOURCE_LANGUAGE['shortname'])
        self.assertEqual(self.translation_api['target_language'],config.GetConfig.DEFAULT_TARGET_LANGUAGE['shortname'])
        self.assertEqual(self.translation_api['text'], config.GetConfig.TEST_ORIGINAL_TEXT)

    def test_api_get(self):
        self.assertEqual(self.translation_api['source_language'], self.translation_api_get['source_language'])
        self.assertEqual(self.translation_api['uid'], self.translation_api_get['uid'])
        self.assertEqual(self.translation_api['target_language'], self.translation_api_get['target_language'])
        self.assertEqual(self.translation_api['text'], self.translation_api_get['text'])

    def test_api_get_non_existing_uid(self):
        self.assertEqual(routes.api_get_translation('nonExistingUID'),{})

    def test_api_get_empty_uid(self):
        self.assertEqual(routes.api_get_translation(''), config.GetConfig.DEFAULT_ERROR_PREFIX+'Field cant be empty.')

    def test_api_get_space_uid(self):
        self.assertEqual(routes.api_get_translation(' '), config.GetConfig.DEFAULT_ERROR_PREFIX+'Field cant be empty.')

    def test_api_get_invalid_type_uid(self):
        self.assertEqual(routes.api_get_translation(37), config.GetConfig.DEFAULT_ERROR_PREFIX+'Invalid field type.')

    def test_api_request_empty_text(self):
        self.assertEqual(routes.api_request_translation(''), config.GetConfig.DEFAULT_ERROR_PREFIX+'Field cant be empty.')

    def test_api_request_space_text(self):
        self.assertEqual(routes.api_request_translation(' '), config.GetConfig.DEFAULT_ERROR_PREFIX+'Field cant be empty.')

    def test_api_request_invalid_type_text(self):
        self.assertEqual(routes.api_request_translation(37), config.GetConfig.DEFAULT_ERROR_PREFIX+'Invalid field type.')


class TestDataBase(unittest.TestCase):
    """
    Class to perform tests to the Database, such as creation of a new translation, fetch a translation and existance
    of the database itself.
    """
    @classmethod
    def setUpClass(self):
        self.translation = models.Translation(config.GetConfig.TEST_ORIGINAL_TEXT,
                                         config.GetConfig.TEST_TRANSLATED_TEXT,
                                         config.GetConfig.REQUESTED_STATUS,
                                         str(config.GetConfig.DEFAULT_SOURCE_LANGUAGE),
                                         str(config.GetConfig.DEFAULT_TARGET_LANGUAGE),
                                         config.GetConfig.TEST_UID
                                         )

        models.db_add_translation_request(self.translation.original_string,
                                          self.translation.uid,
                                          self.translation.source_language,
                                          self.translation.target_language)

    def test_database_existance(self):
        self.assertTrue(engine.connect())

    def test_translation_db_insert(self):
        translation_db = models.db_get_transition(self.translation.uid)

        self.assertEqual(self.translation.original_string, translation_db.original_string.strip())
        self.assertEqual(self.translation.translated_string, translation_db.translated_string.strip())
        self.assertEqual(self.translation.status, translation_db.status.strip())
        self.assertEqual(self.translation.source_language, translation_db.source_language.strip())
        self.assertEqual(self.translation.target_language, translation_db.target_language.strip())
        self.assertEqual(self.translation.uid, translation_db.uid.strip())

    @classmethod
    def tearDownClass(self):
        models.db_delete_translation(self.translation.uid)
        self.translation = None


class TestLocals(unittest.TestCase):
    """
    Class to perform tests on Local variables, Classes and Global variables.
    """
    @classmethod
    def setUpClass(self):
        self.translation = models.Translation(config.GetConfig.TEST_ORIGINAL_TEXT,
                                         config.GetConfig.TEST_TRANSLATED_TEXT,
                                         config.GetConfig.REQUESTED_STATUS,
                                         str(config.GetConfig.DEFAULT_SOURCE_LANGUAGE),
                                         str(config.GetConfig.DEFAULT_TARGET_LANGUAGE),
                                         config.GetConfig.TEST_UID
                                         )

    def test_initial_variables(self):
        page_data = routes.PageData()
        self.assertEqual(routes.active_source_lang, config.GetConfig.DEFAULT_SOURCE_LANGUAGE)
        self.assertEqual(routes.active_target_lang, config.GetConfig.DEFAULT_TARGET_LANGUAGE)
        self.assertEqual(page_data.source_language, config.GetConfig.DEFAULT_SOURCE_LANGUAGE)
        self.assertEqual(page_data.target_language, config.GetConfig.DEFAULT_TARGET_LANGUAGE)
        self.assertEqual(page_data.avail_langs, config.GetConfig.AVAILABLE_LANGUAGES)
        self.assertEqual(page_data.max_text_len, config.GetConfig.MAX_TEXT_LENGTH)
        self.assertEqual(page_data.error_message, "")
        self.assertTrue(len(page_data.data) == 0)

    def test_variables_setter(self):
        sourcelang = {'name':'test','shortname':'t'}
        routes.set_active_source_lang(sourcelang)
        self.assertEqual(routes.active_source_lang,sourcelang)

        targetlang = {'name':'test','shortname':'t'}
        routes.set_active_target_lang(targetlang)
        self.assertEqual(routes.active_target_lang,targetlang)

    def test_translation_creation(self):
        self.assertIsNotNone(self.translation)

    def test_translation_fields(self):
        self.assertEqual(self.translation.original_string, config.GetConfig.TEST_ORIGINAL_TEXT)
        self.assertEqual(self.translation.translated_string, config.GetConfig.TEST_TRANSLATED_TEXT)
        self.assertEqual(self.translation.status, config.GetConfig.REQUESTED_STATUS)
        self.assertEqual(self.translation.source_language, str(config.GetConfig.DEFAULT_SOURCE_LANGUAGE))
        self.assertEqual(self.translation.target_language, str(config.GetConfig.DEFAULT_TARGET_LANGUAGE))
        self.assertEqual(self.translation.uid, config.GetConfig.TEST_UID)

    @classmethod
    def tearDownClass(self):
        self.translation = None


if __name__ == '__main__':
    unittest.main()