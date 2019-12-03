import json


class Index:
    def __init__(self):
        self._vector = dict()
        self._magnitude = 0
        self._is_magnitude_fresh = True

    def calc_magnitude(self):
        sum = 0
        for x in self._vector.values():
            sum += x * x

        sum = sum ** 0.5

        self._magnitude = sum
        self._is_magnitude_fresh = True

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, values_dict):
        if not isinstance(values_dict, dict):
            raise AttributeError("values dict must be a dictionary")

        self._vector = values_dict
        self._is_magnitude_fresh = False

    @vector.deleter
    def vector(self):
        self._vector.clear()
        self._is_magnitude_fresh = False

    def __len__(self):
        return self._magnitude

    @property
    def magnitude(self):
        if self._is_magnitude_fresh:
            return self._magnitude
        else:
            raise ValueError("Magnitude is not fresh. Recalculate before calling")

    @magnitude.setter
    def magnitude(self, value):
        raise TypeError("Magnitude can not be manually set. Call calc_magnitude method instead ")

    def normalize(self):
        if not self._is_magnitude_fresh:
            self.calc_magnitude()

        for key in self.vector:
            self.vector[key] /= self.magnitude

        self._magnitude = 1.0
        self._is_magnitude_fresh = True


class CodeSnippet:
    def __init__(self, lang, snippet):
        self.language = lang
        self.snippet = snippet
        self.index = None

    @property
    def export_object(self):
        obj = {
            "language": self.language,
            "snippet": self.snippet
        }

        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        # return cls(...)
        return None


class APIDoc:
    def __init__(self, url, name, doc_text, code_snippets, out_links, lang):
        self.url = url
        self.name = name
        self.text = doc_text
        self.codes = [CodeSnippet(lang, cs) for cs in code_snippets]
        self.out_links = out_links
        self.index = None

    @property
    def export_object(self):
        obj = {
            "url": self.url,
            "name": self.name,
            "text": self.text,
            "codes": [snip.export_object for snip in self.codes],
            "out_links": json.dumps(self.out_links)
        }
        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)

        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        # return cls(...)
        return None


class Answer:
    def __init__(self, url, text, code_snippets, out_links, upvotes, lang):
        self.url = url
        self.text = text
        self.codes = [CodeSnippet(lang, cs) for cs in code_snippets]
        self.out_links = out_links
        self.upvotes = upvotes
        self.index = None

    @property
    def export_object(self):
        obj = {
            "url": self.url,
            "text": self.text,
            "codes": [snip.export_object for snip in self.codes],
            "out_links": self.out_links,
            "upvotes": self.upvotes
        }

        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        # return cls(...)
        return None


class Question:
    def __init__(self, url, question_id, title, text, code_snippets, out_links, answers, lang):
        self.url = url
        self.id = question_id
        self.title = title
        self.text = text
        self.codes = [CodeSnippet(lang, cs) for cs in code_snippets]
        self.out_links = out_links
        self.answers = answers
        self.index = None

    @property
    def export_object(self):
        obj = {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "codes": [snip.export_object for snip in self.codes],
            "out_links": self.out_links,
            "answers": [ans.export_object for ans in self.answers]
        }

        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        # return cls(...)
        return None


class AnswerIndex:
    def __init__(self, qid, index):
        self.ques_id = qid
        self.text = Index()
        self.code = Index()
        self.others = Index()


class QuestionIndex:
    def __init__(self, ques):
        self.id = ques.id
        self.text_index = Index()
        self.code_index = Index()
        self.others_index = Index()
        self.answers_index = [AnswerIndex(ques.id, ix) for ix in range(len(ques.answers))]
