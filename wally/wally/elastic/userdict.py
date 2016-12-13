from . import constants
import os


class Userdict:
    """Userdict object
    For adding and removing userdict terms for the elasticsearch analyser
    """

    def __init__(self, es_conf_root, user_dictionary_file=constants.JA_USER_DICT):
        # self._es = Elasticsearch()
        self._es_conf_root = es_conf_root
        self._user_dictionary_file = user_dictionary_file
        self._user_dictionary_path = os.path.join(self._es_conf_root, self._user_dictionary_file)

    def update_term_to_userdict(self, term, katakana,
                                term_type=constants.JA_USER_DICT_TERM_TYPE):
        """
        Update existing term (or add new) to userdict which can't be tokenized
        :param term: Term which can't be tokenized e.g. 実女
        :param katakana: Katakana of term ジツジョ
        :param term_type: Type of term e.g. カスタム名詞
        :return: 0 if success
        """
        self.delete_term(term)
        self.update_term_to_userdict(term, katakana, term_type)

    def update_term_split_to_userdict(self, term, term_split, katakana_split,
                                      term_type=constants.JA_USER_DICT_TERM_TYPE):
        """
        Update existing term (or add new) to userdict which can't be tokenized
        :param term: Term e.g. 東京スカイツリー
        :param term_split: Tokenized term e.g. 東京 スカイツリー
        :param katakana_split: Tokenized katakana e.g. トウキョウ スカイツリー
        :param term_type: Type of term e.g. カスタム名詞
        :return: 0 if success
        """
        self.delete_term(term)
        self.update_term_split_to_userdict(term, term_split, katakana_split, term_type)

    def add_term_to_userdict(self, term, katakana, term_type=constants.JA_USER_DICT_TERM_TYPE):
        """
        Add term to userdict which can't be tokenized
        :param term: Term which can't be tokenized e.g. 実女
        :param katakana: Katakana of term ジツジョ
        :param term_type: Type of term e.g. カスタム名詞
        :return: 0 if success
        """
        return self.add_term_split_to_userdict(term, term, katakana, term_type)

    def add_term_split_to_userdict(self, term, term_split, katakana_split, term_type=constants.JA_USER_DICT_TERM_TYPE):
        """
        Add term to userdict
        :param term: Term e.g. 東京スカイツリー
        :param term_split: Tokenized term e.g. 東京 スカイツリー
        :param katakana_split: Tokenized katakana e.g. トウキョウ スカイツリー
        :param term_type: Type of term e.g. カスタム名詞
        :return: 0 if success
        """
        if katakana_split:
            term_to_append = '{0},{1},{2},{3}\n'.format(term, term_split, katakana_split, term_type)
            with open(self._user_dictionary_path, 'a') as fp:
                fp.write(term_to_append)
            return 0
        return 1  # No katakana pronunciation provided

    def delete_term(self, term):
        """
        Delete term-line in userdict. If multiple in userdict - all occurrences are deleted
        :param term: Term in userdict to delete (not splitted)
        :return: 0 if success
        """
        # Read content and search in lines
        with open(self._user_dictionary_path, 'r') as fp:
            content = fp.readlines()
            found_idx = [idx for idx, line in enumerate(content) if line.startswith(term)]

        # Delete lines with terms
        if len(found_idx) > 0:
            content = [i for j, i in enumerate(content) if j not in found_idx]
            # Rewrite content without lines
            with open(self._user_dictionary_path, 'w') as fp:
                fp.writelines(content)

        return 0
