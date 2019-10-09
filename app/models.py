from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
from sqlalchemy.sql.expression import func, desc
from database import db_session, metadata, engine
import config


class Translation(object):
    """
    Class of the translation object. It contains all the information needed about a translation, referencing all the
    columns in the DB_TRANSLATIONS_TABLE_NAME table.

    Every time a new translation is requested, this object is instantiated and added to the database.
    """
    metadata.clear()
    query = db_session.query_property()

    def __init__(self, original_string=None, translated_string=None, status=None, source_language=None,
                 target_language=None, uid=None):
        self.original_string = original_string
        self.translated_string = translated_string
        self.status = status
        self.source_language = source_language
        self.target_language = target_language
        self.uid = uid

    def __repr__(self):
        """
        Visual representation of the translation itself.

        The values associated to each column of the database, are separated by a character (DEFAULT_COLUMN_SEPARATOR)
        to be accessed in the html templates.
        :return:
        """
        return '' \
               + self.original_string + config.GetConfig.DEFAULT_COLUMN_SEPARATOR \
               + self.translated_string + config.GetConfig.DEFAULT_COLUMN_SEPARATOR \
               + self.status + config.GetConfig.DEFAULT_COLUMN_SEPARATOR \
               + self.source_language + config.GetConfig.DEFAULT_COLUMN_SEPARATOR \
               + self.target_language


# variable that holds the information about the dataset in the DB_TRANSLATIONS_TABLE_NAME table.
translations = Table(config.GetConfig.DB_TRANSLATIONS_TABLE_NAME, metadata,
                     Column('id', Integer, primary_key=True),
                     Column('original_string', String(500), unique=True),
                     Column('translated_string', String(500), unique=True),
                     Column('status', String(50), unique=True),
                     Column('source_language', String(50), unique=True),
                     Column('target_language', String(50), unique=True),
                     Column('uid', String(50), unique=True)
                     )

mapper(Translation, translations)


def db_add_translation_request(text, uid, sourcelang, targetlang):
    """
    Add a new translation to the database.

    Adds the REQUESTED_STATUS as status, the @sourcelang as source_language and @targetlang as target_language
    :param text: string variable to be translated by the API (the text in the source language)
    :param uid: identifier of the translation request (attributed and received by the API)
    :param sourcelang: active source language (the same language of the input text)
    :param targetlang: active target language (the language to which the text is going to be translated)
    :return:
    """
    new_translation_req = Translation(text, '', config.GetConfig.REQUESTED_STATUS, sourcelang, targetlang, uid)
    db_session.add(new_translation_req)
    db_session.commit()


def db_set_translated_string(uid, translated_text):
    """
    Update the translated text for a specific translation on the database.
    :param uid:  unique identifier associated with each translation (attributed and returned by the API).
    :param translated_text: translated text returned by the API.
    """
    translation = Translation.query.filter(Translation.uid == uid)
    translation.update({"translated_string": translated_text})
    db_session.commit()


def db_set_translation_status(uid, status):
    """
    Update a status for a specific translation on the database.
    :param uid:  unique identifier associated with each translation (attributed and returned by the API)
    :param status: new status to attribute to the translation
    """
    translation = Translation.query.filter(Translation.uid == uid)
    translation.update({"status": status})
    db_session.commit()


def db_get_all_translations():
    """
    function that queries the database for all the translations, and order them by descending order of length(translated_string).
    :return translations: Array with the ordered translations
    """
    translations = Translation.query.order_by(desc(func.length(Translation.translated_string))).all()
    return translations


def db_get_all_not_closed_translations():
    """
    Function to get an array of all the translations which are not closed (Status != from 'Translated')
    :return translation: Returns the array of translations if they exist, otherwise return a string 'Not found.'
    """
    translation = Translation.query.filter(Translation.status != config.GetConfig.TRANSLATED_STATUS).all()
    if (len(translation) > 0):
        return translation
    else:
        return 'Not Found.'


def db_get_transition(uid):
    """
    Function to get a specific translation from the database.
    :param uid: unique identifier associated with each translation (attributed and returned by the API)
    :return translation[0]: First occurrence of the query, (because the uid is UNIQUE, there is always going to be only 1
    or 0 occurrences). Returns a string 'Not Found.' if no occurrences are found for the uid.
    """
    translation = Translation.query.filter(Translation.uid == uid).all()
    if len(translation) > 0:
        return translation[0]
    else:
        return 'Not Found.'


def db_delete_translation(uid):
    """
    Delete a translation from the database.
    :param uid: unique identifier associated with each translation (attributed and returned by the API)
    """
    delete = translations.delete().where(translations.columns.uid == uid)
    engine.execute(delete)
