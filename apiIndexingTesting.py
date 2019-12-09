import parser
import models
import indexer

apiDoc = './dataset/API/raw/docs/api/java.base/java/io/BufferedInputStream.html'

jsonDoc = parser.parse_API_doc_driver(apiDoc)

docObject = models.APIDoc.from_json(jsonDoc)

index = indexer.index_api_doc(docObject)

methods_index = index.methods_index
print(index.combined_code_index.vector)
# for method_index in methods_index:
    # print(method_index.text_index.vector)
    # print(method_index.code_index.vector)

    # print('-----')
