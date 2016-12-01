from email import policy
import email
import email.message as message
import json
import cld2
import os
from . import constants


class MailExtractor:
    """Mailextractor

    Convert email-file to json-file
    Classifies its content language with a reliability
    """

    def __init__(self, func=None):
        self.cnt_total = 0
        self.errors_convert = []

    def extract_jsons(self, files):
        """
        Generator: Convert multiple files into jsons applying the generator pattern
        State-variables cnt_total and erros on class MailExtractor will be updated

        :param files: Any iterable, generator preferred for optimal memory usage
        :return: Tuples (Generator-Iterable) of (Id, E-mail JSON)
        """

        # Reset coutners
        self.cnt_total = 0
        self.errors_convert = []

        for file in files:
            self.cnt_total += 1
            try:
                yield (os.path.basename(file), self.extract_json(file))  # id, data
            except (LookupError, AttributeError, ValueError, TypeError, FileNotFoundError) as e:
                errmsg = 'An exception of type {0} occured, when reading file {1}: {2}'.format(
                    type(e).__name__, file, e)
                #print(errmsg)  # TODO: Remove this later!
                self.errors_convert.append(errmsg)
                continue
                #yield (constants.ERROR_EXTRACT, errmsg)

    @staticmethod
    def extract_json(file):
        """
        Convert file into json
        :param file: Path to a file which can be read (File will be opened here)
        :return: JSON-String
        """

        with open(file, 'rb') as fp:  # read as byte-string
            msg = email.message_from_binary_file(fp, policy=policy.default)

        jsonstr = json.dumps(msg, sort_keys=True, indent=4, ensure_ascii=False, cls=EmailMessageEncoder)
        return jsonstr


def _extract_body_plain_text(msg):
    bodyplain = msg.get_body(preferencelist='plain')
    if bodyplain is not None:
        return bodyplain.get_content()

    htmlbody = msg.get_body(preferencelist='html')
    if htmlbody is not None:
        html = htmlbody.get_content()
        plain = html  # TODO: Html-Escaping
        return plain

    return None


def is_preferred_lang(lang_details):
    return (lang_details.language_code == constants.PREFERRED_LANG) & (
        lang_details.percent >= constants.PREFERRED_THRESHOLD)


def select_language(text):
    lang_is_reliable, text_bytes_found, lang_details_list = cld2.detect(text)

    lang_selected_details = next((x for x in lang_details_list if is_preferred_lang(x)), None)

    # If preferred language not significant enough, use language with highest percentage
    if lang_selected_details is None:
        lang_selected_details = lang_details_list[0]

    return lang_selected_details


class EmailMessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, message.Message):
            from_tup = email.utils.parseaddr(obj['from'])
            to_tup = email.utils.parseaddr(obj['to'])
            replyto_tup = email.utils.parseaddr(obj['reply-to'])
            sent = email.utils.parsedate_to_datetime(obj['date'])
            date_time_no_millis = ('{:' + constants.JSON_DATETIME_FORMAT + '}').format(sent)
            # (https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#built-in-date-formats)
            # date_time_no_millis -> yyyy-MM-dd'T'HH:mm:ssZZ
            # or custom format: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html

            body_plain = _extract_body_plain_text(obj)

            # detect language
            lang_selected_details = select_language(body_plain)
            lang_detected_code = lang_selected_details.language_code
            lang_percent = lang_selected_details.percent

            return {
                'fromName': from_tup[0],
                'fromEmail': from_tup[1],
                'toName': to_tup[0],
                'toEmail': to_tup[1],
                'replyToName': replyto_tup[0],
                'replyToEmail': replyto_tup[1],
                'subject': obj['subject'],
                'date': date_time_no_millis,  # obj['date']
                'body': body_plain,
                'langCode': lang_detected_code,
                'langPercent': lang_percent
            }
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    import codecs
    inDir = 'data_in'
    outDir = 'data_out'

    print("Start reading emails from folder {0}...".format(inDir))

    cnt = 0
    cntErr = 0
    basepath = os.getcwd()
    inPath = os.path.join(basepath, inDir)
    for filename in os.listdir(inPath):
        if os.path.isdir(os.path.join(inPath, filename)):
            continue
        mail = filename
        f = os.path.join(basepath, inDir, mail).replace('\\', '/')
        outf = os.path.join(basepath, outDir, ''.join([mail, str(cnt), '.txt']))

        try:
            ret = MailExtractor().extract_json(f)
        except (LookupError, AttributeError, ValueError, TypeError) as e:
            # TODO: Print Type of Exception!
            ret = 'Error when reading file {0}: {1}'.format(filename, e)
            cntErr += 1
            print(ret)

        with codecs.open(outf, 'w', 'utf-8') as outfp:
            outfp.write(ret)

            # for key, value in message.items():
            #    print('{0}: {1}'.format(key, value))
            # file.write('{0}: {1}\n'.format(key, value))

        cnt += 1

    print("Successfully read {0}/{1} emails, output to folder {2}".format(cnt - cntErr, cnt, outDir))
