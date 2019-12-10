import os

import log
import parser
import models
import indexer
from starter import init, end
import pickler
import shared

if __name__ == "__main__":
    init()

    index_dict = dict()
    api_list = os.listdir('./dataset/API/parsed/')

    ix = 0
    for aj in api_list:
        ix += 1
        if ix % 500 == 0:
            log.debug(f"Completed {ix}")
            input()

        aj = os.path.join('./dataset/API/parsed', aj)
        apiJson = None
        with open(aj) as f:
            apiJson = f.read()

        docObject = models.APIDoc.from_json(apiJson)

        index = indexer.index_api_doc(docObject)

        methods_index = index.methods_index
        index_dict[docObject.name.snippet] = index

    pickler.write_api_index(index_dict)
    indexer.calculate_all_idf()
    end()
