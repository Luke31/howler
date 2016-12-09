import re
from email.header import decode_header
from . import constants


def extract_body_plain_text(msg):
    """
    Get body of message (first choice plain, second html)
    :param msg: email.message.Message
    :return: body of message (plain/html)
    """
    bodyplain = msg.get_body(preferencelist='plain')
    if bodyplain is not None:
        return bodyplain.get_content()

    htmlbody = msg.get_body(preferencelist='html')
    if htmlbody is not None:
        html = htmlbody.get_content()
        plain = html  # TODO: Html-Escaping
        return plain

    return None


def has_attachment(msg):
    """
    Check if the message has one or more attachments
    :param msg: email.message.Message
    :return: Tuple (has_attachment, attachment_names)
    True if msg has one or more attachment
    attachment_names: Names of attachments as string
    """
    body = msg.get_body()
    filenames = []
    try:
        for part in msg.iter_attachments():
            fn = part.get_filename()
            if fn is None:
                fn = constants.NO_FILENAME
            filenames.append(fn)
    except AttributeError as exc:
        return False, ''  # 'str' object has no attribute 'is_attachment'

    return len(filenames) > 0, ', '.join(filenames)


invalid_encoded_words = r"(=\?.*\?=)(?=\S)"
invalid_encoded_words_bytes = br"(=\?.*\?=)(?=\S)"


def fix_wrong_encoded_words_header(header_value):
    """
    Ensure Mime Encoded Words end with a white-space, if not, insert one.
    MIME Encoded Words: 'encoded-word' that appears in a 'comment' MUST be separated from
    any adjacent 'encoded-word' or 'ctext' by 'linear-white-space' (https://tools.ietf.org/html/rfc2047#section-5)

    :param header_value: Header value string to fix
    :return: Valid MIME Encoded Word string
    """
    fixed_header_value = re.sub(r"(=\?.*\?=)(?=\S)", r"\1 ", header_value)

    if fixed_header_value == header_value:  # nothing needed to fix
        return header_value
    else:
        dh = decode_header(fixed_header_value)
        default_charset = 'unicode-escape'
        correct_header_value = ''.join([str(t[0], t[1] or default_charset) for t in dh])
        return correct_header_value


def fix_wrong_encoded_words_header_body(fp):
    file_content = fp.read()
    pat = re.compile(invalid_encoded_words_bytes)
    try:
        fixed_file_content = pat.match(file_content)
    except Exception as e:
        print(e)
    return fixed_file_content
