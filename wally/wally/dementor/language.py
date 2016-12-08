from . import constants
import cld2


def detect_select_language(text):
    """
    Detects language of input text. If determined langauge is preferred language (ja), return this.
    If not return language with highest score.

    :param text: Text to analyze langauge of
    :return: (tuple of Detection) – A namedtuple of (language_name, language_code, percent, score).
    language_name is the internal CLD2 name for the language.
    language_code is a ISO 639-1 lanuguage code.
    percent is what percentage of the original text was detected as.
    score is the confidence score for that language.
    """
    lang_is_reliable, text_bytes_found, lang_details_list = cld2.detect(text)

    # Check if preferred language is available
    lang_selected_details = next((x for x in lang_details_list if _is_preferred_lang(x)), None)

    # If preferred language not significant enough, use language with highest percentage
    if lang_selected_details is None:
        lang_selected_details = lang_details_list[0]

    return lang_selected_details


def _is_preferred_lang(lang_details, preferred_lang=constants.PREFERRED_LANG,
                       preferred_lang_threshold=constants.PREFERRED_LANG_THRESHOLD):
    return (lang_details.language_code == preferred_lang) & (
        lang_details.percent >= preferred_lang_threshold)
