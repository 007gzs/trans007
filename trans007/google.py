import requests


class GoogleTranslate:
    GOOGLE_TRANSLATE_TKK = "448487.932609646"
    GOOGLE_TKK_INDEX, GOOGLE_TKK_KEY = map(int, GOOGLE_TRANSLATE_TKK.split('.'))

    LANGS = (
        'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg', 'ca', 'ceb', 'ny',
        'zh-CN', 'zh-TW', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy',
        'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga',
        'it', 'ja', 'jv', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv', 'ln', 'lt',
        'lg', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-Mtei', 'lus', 'mn', 'my', 'ne', 'no', 'or',
        'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st', 'sn', 'sd', 'si',
        'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'ak', 'uk',
        'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
    )

    def __init__(self, proxies=None):
        self.proxies = proxies

    @classmethod
    def shift_left_or_right_then_sum_or_xor(cls, num, opt_string):
        for i in range(0, len(opt_string) - 2, 3):
            acc = opt_string[i + 2]
            if 'a' <= acc:
                acc = ord(acc) - 87
            else:
                acc = int(acc)
            if opt_string[i + 1] == '+':
                acc = num >> acc
            else:
                acc = num << acc
            if opt_string[i] == '+':
                num += acc & 0xffffffff
            else:
                num ^= acc
            num &= 0xffffffff
        return num

    @classmethod
    def transform_query(cls, query):
        bytes_array = []
        i = 0
        while i < len(query):
            char_code = ord(query[i])
            if 128 > char_code:
                bytes_array.append(char_code)
            else:
                if 2048 > char_code:
                    bytes_array.append((char_code >> 6) | 0xc0)
                else:
                    if 0xd800 == (char_code & 0xfc00) and i + 1 < len(query) and 0xdc00 == (query[i + 1] & 0xfc00):
                        i += 1
                        char_code = 0x10000 + ((char_code & 0x3ff) << 10) + (query.charCodeAt(++i) & 0x3ff)
                        bytes_array.append((char_code >> 18) | 0xf0)
                        bytes_array.append(((char_code >> 12) & 63) | 0x80)
                    else:
                        bytes_array.append((char_code >> 12) | 0xe0)
                    bytes_array.append(((char_code >> 6) & 0x3f) | 0x80)
                bytes_array.append((char_code & 0x3f) | 0x80)
            i += 1
        return bytes_array

    @classmethod
    def calc_hash(cls, query):
        """
        Calculates the hash (TK) of a query for google translator.
        :param query:
        :return:
        """
        bytes_array = cls.transform_query(query)
        encoding_round = cls.GOOGLE_TKK_INDEX
        for item in bytes_array:
            encoding_round += item
            encoding_round = cls.shift_left_or_right_then_sum_or_xor(encoding_round, "+-a^+6")

        encoding_round = cls.shift_left_or_right_then_sum_or_xor(encoding_round, "+-3^+b+-f")
        encoding_round ^= cls.GOOGLE_TKK_KEY
        if encoding_round <= 0:
            encoding_round = (encoding_round & 0x7fffffff) + 0x80000000
        normalized_result = encoding_round % 1000000
        return f"{normalized_result}.{normalized_result ^ cls.GOOGLE_TKK_INDEX}"

    def request(self, method, url, data=None, params=None, **kwargs):
        kwargs.setdefault('proxies', self.proxies)
        return requests.request(method, url, params=params, data=data, timeout=10, **kwargs)

    def translate(self, text, source_language, target_language):
        assert source_language in self.LANGS and target_language in self.LANGS
        res = self.request(
            'POST',
            "https://translate.googleapis.com/translate_a/t",
            params={
                'anno': 3,
                'client': 'te',
                'v': '1.0',
                'format': 'html',
                'sl': source_language,
                'tl': target_language,
                'tk': self.calc_hash(text),
            },
            data={
                'q': text
            }
        )
        result = res.json()[0]
        idx = 0
        sentences = []
        while True:
            sentence_start_index = result.find("<b>", idx)
            if sentence_start_index < 0:
                break
            sentence_final_index = result.find("<i>", sentence_start_index)
            if sentence_final_index < 0:
                sentences.append(result[sentence_start_index + 3:])
                break
            else:
                sentences.append(result[sentence_start_index + 3:sentence_final_index])
            idx = sentence_final_index
        if sentences:
            result = " ".join(sentences)
        result = result.replace("</b>", "")

        return result

