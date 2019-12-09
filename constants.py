question_replaceable_special_characters = {',', '//', "'", '"', ';', '?', ':', '-', '(', ')', '[', ']', '{', '}', '$',
                                           '#',
                                           '=',
                                           '<', '>'}
code_replaceable_special_characters = {',', '//', "'", '"', ';', '?', ':', '-', '(', ')', '[', ']', '{', '}', '$', '#',
                                       '=',
                                       '<', '>'}
special_characters = ['*', '$']
punctuations = set()
pickle_data_dir = "bin/data"
pickled_questions_dir = "bin/data/questions"
pickled_api_dir = "bin/data/docs"
pickle_files_extension = ".pickle"
questions_per_segment = 100
apis_per_segment = 200
debug_print_len = 25
question_title_weight = 2
log_base = 10

# postgres params
postgres_host = "127.0.0.1"
postgres_db = "ir"
postgres_user = "ir_admin"
postgres_password = "minda"
