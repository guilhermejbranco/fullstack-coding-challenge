from flask import Flask, render_template, request, make_response
import models
from multiprocessing.dummy import Pool as ThreadPool
import config
import requests
import sass
import ast

# Global variables
active_source_lang = config.GetConfig.DEFAULT_SOURCE_LANGUAGE
active_target_lang = config.GetConfig.DEFAULT_TARGET_LANGUAGE


# Classes
class PageData:
    """
    Class holding the values to be used in the html template.

    @data is an array with all the translations in the database (in the dict form).
    @error_message is the message that is going to be displayed in the frontend in case of an error. When an exception
    occurs, this value should be changed to the details of the error.
    """
    page_title = config.GetConfig.DEFAULT_PAGE_TITLE
    data = []
    data_len = 0
    source_language = active_source_lang
    target_language = active_target_lang
    avail_langs = config.GetConfig.AVAILABLE_LANGUAGES
    avail_langs_len = len(config.GetConfig.AVAILABLE_LANGUAGES)
    max_text_len = config.GetConfig.MAX_TEXT_LENGTH
    column_separator = config.GetConfig.DEFAULT_COLUMN_SEPARATOR
    error_message = ''
    port = config.GetConfig.DEFAULT_PORT
    url = config.GetConfig.DEFAULT_URL


# Initialization of the flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def api_request_translation(text):
    """
    function that requests a new translation of the string @text to the API.

    It uses always the values stored in active_source_lang and active_target_lang, to use in the language_pair structure.
    Those values are changed in the frontend, when the user chooses different languages to translate.

    :param text: string with the text to be translated.
    """
    if(type(text) is not str):
        return config.GetConfig.DEFAULT_ERROR_PREFIX + 'Invalid field type.'
    if(len(text.strip()) < 1):
        return config.GetConfig.DEFAULT_ERROR_PREFIX + 'Field cant be empty.'

    data = {'text': text,
            'source_language': active_source_lang['shortname'],
            'target_language': active_target_lang['shortname']}

    result = requests.post(
        config.GetConfig.API_POST_TRANSLATION_URL,
        json=data,
        headers={'Authorization': 'ApiKey ' + config.GetConfig.API_USERNAME + ':' + config.GetConfig.API_KEY,
                 'Content-Type': 'application/json'}
    )

    if result:
        return result.json()
    else:
        print('An error has occurred while requesting translation. ' + result.text)
        return config.GetConfig.DEFAULT_ERROR_PREFIX + result.text


def api_get_translation(uid):
    """
    function that gets a translation from the API, with the uid = @uid.
    :param uid: uid of the translation requested. This field is verified to make sure it's not invalid.
    """
    if(type(uid) is not str):
        return config.GetConfig.DEFAULT_ERROR_PREFIX + 'Invalid field type.'
    if(len(uid.strip()) < 1):
        return config.GetConfig.DEFAULT_ERROR_PREFIX + 'Field cant be empty.'

    result = requests.get(
        config.GetConfig.API_GET_TRANSLATION_URL + uid,
        headers={'Authorization': 'ApiKey ' + config.GetConfig.API_USERNAME + ':' + config.GetConfig.API_KEY,
                 'Content-Type': 'application/json'}
    )

    if result:
        return result.json()
    else:
        print('An error has occurred while getting translation. ' + result.text)
        return config.GetConfig.DEFAULT_ERROR_PREFIX + result.text


def update_translations_worker(translation):
    """
    Thread function to get an update on a @translation that is in the database, and that has yet to be translated.

    If the status has changed, the value on the database is updated, as well as the translated_text itself.

    It also changes the default values of status (received from the API), to the defined strings in the config.py file.

    :param translation: translation object fetched from the database.
    """
    uid = translation.uid.strip()

    if uid:
        updatedtranslation = api_get_translation(uid)

        if 'translatedText' in updatedtranslation:
            models.db_set_translated_string(uid, updatedtranslation['translatedText'])
        if updatedtranslation['status'] == 'new':
            models.db_set_translation_status(uid, config.GetConfig.REQUESTED_STATUS)
        elif updatedtranslation['status'] == 'completed':
            models.db_set_translation_status(uid, config.GetConfig.TRANSLATED_STATUS)
        else:
            models.db_set_translation_status(uid, config.GetConfig.PENDING_STATUS)



def update_translations():
    """
    Function that gets all the translations in the database, that don't have the state = TRANSLATED_STATUS, and creates
    a thread for each translation, to the function update_translations_worker().
    """
    translations = models.db_get_all_not_closed_translations()

    if len(translations) > 0 and type(translations) is not str:
        pool = ThreadPool(len(translations))
        pool.map(update_translations_worker, translations)



def generate_page_data():
    """
    Function that generates the data necessary to the html templates, such as, translations to display, languages available,
    etc.

    It also handles the data saved in the cookies, fetching the values associated with each key.
    """
    translations = models.db_get_all_translations()
    page_data = PageData()
    page_data.data = translations
    if('targetlanguage' in request.cookies):
        targetlang = ast.literal_eval(request.cookies.get('targetlanguage').strip())
        page_data.target_language = targetlang
        set_active_target_lang(targetlang)
    if ('sourcelanguage' in request.cookies):
        sourcelang = ast.literal_eval(request.cookies.get('sourcelanguage').strip())
        page_data.source_language = sourcelang
        set_active_source_lang(sourcelang)
    page_data.data_len = len(translations)
    return page_data


def set_active_source_lang(language):
    global active_source_lang
    active_source_lang = language


def set_active_target_lang(language):
    global active_target_lang
    active_target_lang = language

# Function to compile scss files to css
def compile_scss():
    sass.compile(dirname=('assets/scss', 'static/css'))


# Add a watcher to the changes in app files
#server = Server(app.wsgi_app)
#server.watch('assets/scss/*.scss', compile_scss)
#server.watch('templates/*.html')


@app.template_filter()
def string_split(value, char):
    """
    Jinja2 filter to split a string @value by a character @char and return the array
    e.g. string_split('One;Two;Three',';') = ['One','Two','Three']
    """
    return str(value).split(char)


@app.route('/')
def root():
    page_data = generate_page_data()
    update_translations()
    return render_template('home.html', page_data=page_data)


@app.route('/changelang', methods=['POST', 'GET'])
def changelang():
    """
    Function that changes the language to the value received from the frontend, stored in the variable request.form.

    Firstly, changes the global variable of each source and target language (if they are different from the current value),
    and of the page_data() generated to be displayed in the render_template.
    Then, creates a response object, with the render_template instance, and adds two (key, value) pairs to the cookie
    storage, holding the current source and target language selected.
    :return:
    """
    if request.method == 'POST':
        targetlang = request.form.getlist('targetlanguage')
        sourcelang = request.form.getlist('sourcelanguage')

        page_data = generate_page_data()

        if len(targetlang) > 0:
            page_data.target_language = ast.literal_eval(targetlang[0])
            set_active_target_lang(ast.literal_eval(targetlang[0]))

        if len(sourcelang) > 0:
            page_data.source_language = ast.literal_eval(sourcelang[0])
            set_active_source_lang(ast.literal_eval(sourcelang[0]))

        resp = make_response(render_template("home.html", page_data=page_data))

        if len(targetlang) > 0:
            resp.set_cookie("targetlanguage", targetlang[0])

        if len(sourcelang) > 0:
            resp.set_cookie("sourcelanguage", sourcelang[0])
        return resp

    elif request.method == 'GET':
        page_data = generate_page_data()
        return render_template('home.html', page_data=page_data)


@app.route('/home', methods=['POST', 'GET'])
def homepage():
    """
    Function that is responsible to receive a new translation request (e.g. when the user enters text to translate and
    presses the submit button).

    If the request is successful, the function adds the new request to the database and renders a new template, otherwise,
    it generates a new error message with the details of the exception received.
    """
    if request.method == 'POST':
        text = request.form.getlist('String')[0]
        translation = api_request_translation(text)
        if config.GetConfig.DEFAULT_ERROR_PREFIX in translation:
            page_data = generate_page_data()
            if 'error_message' in translation.split(config.GetConfig.DEFAULT_ERROR_PREFIX)[1]:
                page_data.error_message = ast.literal_eval(translation.split(config.GetConfig.DEFAULT_ERROR_PREFIX)[1])['error_message']
            else:
                page_data.error_message = ast.literal_eval(translation.split(config.GetConfig.DEFAULT_ERROR_PREFIX)[1])['error']
            return render_template("home.html", page_data=page_data)
        uid = translation["uid"]
        models.db_add_translation_request(text.strip(), uid.strip(),active_source_lang['name'],active_target_lang['name'])
        page_data = generate_page_data()
        return render_template("home.html", page_data = page_data)
    elif request.method == 'GET':
        page_data = generate_page_data()
        return render_template('home.html', page_data=page_data)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def __init__(self, title, post_text):
    self.title = title
    self.post_text = post_text


if __name__ == '__main__':
    app.run(port=config.GetConfig.DEFAULT_PORT)
