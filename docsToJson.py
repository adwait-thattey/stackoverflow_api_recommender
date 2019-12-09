import parser
import os
import re
import models

raw_path = './dataset/API/raw/docs'
parsed_path = './dataset/API/parsed/'

# Ignore css, zip, gif,

count = 0

for (dirName, subdirList, fileList) in os.walk(raw_path, topdown=False):

    for fname in fileList:
        # print(type(fname))
        if(re.search('.html$',fname) or re.search('.HTML$',fname)):
            count+=1
            # print(fname)

            full_fname = os.path.join(dirName,fname)
            print(full_fname)

            try:
                jsonString = parser.parse_API_doc_driver(full_fname)
                # printjsonString)

                new_doc = models.APIDoc.from_json(jsonString)

                for method in new_doc.methods:
                    print(method.method_sig.snippet)
                # print(new_doc.text)

                filename = os.path.join(parsed_path,fname.replace('.html','.json'))

                f = open(filename, "w")
                f.write(jsonString)
                f.close()
                print(filename+' successful !')


            except:

                print(fname+' failed !')

    # if count%100 == 0:
    #     s = input()
    print('-------')

print(str(count)+" files processed")
#     if(count==10): break
# print(count)
