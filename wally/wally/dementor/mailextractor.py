from email import policy
import email
import email.message as message
import json
import os
from . import constants
from . import language
from . import helpers_mail


class MailExtractor:
    """Mailextractor

    Convert email-file to json-file or multiple
    Classifies its content language and adds it to the json
    Development based on mail formats: RFC 822, RFC 2822, RFC 5322
    Attachment is ignored in this version
    """

    def __init__(self):
        self.cnt_total = 0
        self.errors_convert = []

    def extract_jsons(self, files):
        """
        Generator: Convert multiple mail-files into jsons applying the generator pattern
        State-variables cnt_total and erros on class MailExtractor will be updated

        :param files: Any iterable, generator preferred for optimal memory usage
        :return: Tuples (Generator-Iterable) of (Id, E-mail JSON-String)
        """

        # Reset counters
        self.cnt_total = 0
        self.errors_convert = []

        for file in files:
            self.cnt_total += 1
            try:
                yield (os.path.basename(file), self.extract_json(file))  # id, data
            except (LookupError, AttributeError, ValueError, TypeError, FileNotFoundError, AssertionError) as exc:
                errmsg = 'An exception of type {0} occured, when reading file {1}: {2}'.format(
                    type(exc).__name__, file, exc)
                self.errors_convert.append(errmsg)
                continue

    @staticmethod
    def extract_json(file):
        """
        Convert mail-file into json
        :param file: Path to a file which can be read (File will be opened here)
        :return: JSON-String
        """

        with open(file, 'rb') as fp:  # read as byte-string
            msg = email.message_from_binary_file(fp, policy=policy.default)

        jsonstr = json.dumps(msg, sort_keys=True, indent=4, ensure_ascii=False, cls=EmailMessageEncoder)
        return jsonstr


class EmailMessageEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder for converting email.message.Message to json-string
    """

    def default(self, obj):
        if isinstance(obj, message.Message):
            from_tup = email.utils.parseaddr(obj['from'])
            to_tup = email.utils.parseaddr(obj['to'])
            replyto_tup = email.utils.parseaddr(obj['reply-to'])
            sent = email.utils.parsedate_to_datetime(obj['date'])
            date_time_no_millis = ('{:' + constants.JSON_DATETIME_FORMAT + '}').format(sent)
            # (https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#built-in-date-formats   )
            # date_time_no_millis -> yyyy-MM-dd'T'HH:mm:ssZZ
            # or custom format: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html

            # Get subject, fix MIME Encoded Words and decode again
            subject = helpers_mail.fix_wrong_encoded_words_header(obj['subject'])
            body_plain = helpers_mail.extract_body_plain_text(obj)
            text_combined = ''.join((subject, ' ', body_plain))  # Analyze text of subject and body

            # detect language
            lang_selected_details = language.detect_select_language(text_combined)
            lang_detected_code = lang_selected_details.language_code
            lang_percent = lang_selected_details.percent

            (has_attachment, attachment_names) = helpers_mail.has_attachment(obj)

            return {
                'fromName': from_tup[0],
                'fromEmail': from_tup[1],
                'toName': to_tup[0],
                'toEmail': to_tup[1],
                'replyToName': replyto_tup[0],
                'replyToEmail': replyto_tup[1],
                'subject': subject,
                'date': date_time_no_millis,  # obj['date']
                'body': body_plain,
                'langCode': lang_detected_code,
                'langPercent': lang_percent,
                'spam': 0,  # TODO: Check if spam
                'hasAttachment': has_attachment,
                'attachmentNames': attachment_names,
            }
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
