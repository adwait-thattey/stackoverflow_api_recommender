import json
from unidecode import unidecode

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
        obj = self.snippet

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
    def __init__(self, qid):
        self.ques_id = qid
        self.text = Index()
        self.code = Index()
        self.others = Index()


class QuestionIndex:
    def __init__(self, ques):
        self.id = ques.id
        self.title_index = Index()
        self.text_index = Index()
        self.code_index = Index()
        self.others_index = Index()
        self.answers_index = list()

class APIField:
    def __init__(self, field_name, field_sig, description):
        self.field_name = CodeSnippet("java", field_name)
        self.field_sig = CodeSnippet("java", field_sig)
        self.description = description

    @property
    def export_object(self):
        obj = {
            "field_name" : self.field_name.export_object,
            "field_sig" : self.field_sig.export_object,
            "description" : self.description
        }
        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        obj = json.loads(json_string)
        return cls(obj['field_name'],obj['field_sig'],obj['description'])
        return None

class APIMethod:
    def __init__(self, method_name, method_sig, description):
        self.method_name = CodeSnippet("java", method_name)
        self.method_sig = CodeSnippet("java", method_sig)
        self.description = description

    @property
    def export_object(self):
        obj = {
            "method_name" : self.method_name.export_object,
            "method_sig" : self.method_sig.export_object,
            "description" : self.description
        }
        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        obj = json.loads(json_string)
        return cls(obj['method_name'],obj['method_sig'],obj['description'])
        return None

class APIDoc:
    def __init__(self, name, module, package, doc_text, code_snippets, lang='java'):

        self.name = CodeSnippet("java", name)
        self.module = CodeSnippet("java", module)
        self.package = CodeSnippet("java", package)
        self.text = doc_text
        code_snippets = [unidecode(cs) for cs in code_snippets]
        self.codes = [CodeSnippet(lang, cs) for cs in code_snippets]
        self.index = None
        self.fields = list()
        self.methods = list()


    def add_field(self, field_name, field_signature, description):
        field = APIField(field_name=field_name, field_sig=field_signature, description=description)
        self.fields.append(field)

    def add_method(self, method_name, method_signature, description):
        method_signature = unidecode(method_signature)
        method = APIMethod(method_name=method_name, method_sig=method_signature, description=description)
        self.methods.append(method)

    @property
    def export_object(self):
        obj = {
            "name": self.name.export_object,
            "module": self.module.export_object,
            "package": self.package.export_object,
            "text": self.text,
            "codes": [snip.export_object for snip in self.codes],
            "fields": [field.export_object for field in self.fields],
            "methods" : [method.export_object for method in self.methods]
        }
        return obj

    def to_json(self):
        json_string = json.dumps(self.export_object)
        return json_string

    @classmethod
    def from_json(cls, json_string):
        # parse json and return object of class
        print('In from_json..')
        data = json.loads(json_string)
        print(data)
        obj = cls(data['name'],data['module'],data['package'],data['text'],data['codes'])

        for field in data['fields']:
            obj.add_field(field['field_name'],field['field_sig'],field['description'])


        for method in data['methods']:
            obj.add_method(method['method_name'],method['method_sig'],method['description'])

        return obj
        return None
