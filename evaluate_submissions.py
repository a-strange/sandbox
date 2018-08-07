import os
import re
import csv

import pandas as pd


FILE_LOC = 'Submissions'
ANSWER_FILE = 'test_policies_with_answers.csv'
BASE_PATTERN = "([a-zA-Z]*)-{}-01Vanilla.pkl"
MODEL_PATTERN = "-([a-zA-Z]{2})-"


MODELS = ['LM', 'GLM', 'ML']


answers = pd.read_csv(ANSWER_FILE)
sum_e_n = sum(answers['E[N]'])
sum_e_x = sum(answers['E[X]'])


def determine_model(file_name):
    return re.findall(MODEL_PATTERN, file_name)[0]


def determine_scientist(file_name, model):
    name_pattern = BASE_PATTERN.format(model)
    return re.findall(name_pattern, file_name)[0]


def submission_results(file_location):
    submission = pd.read_pickle(submitted_file)
    e_n = sum(submission['E[N]'])
    e_x = sum(submission['E[X]'])
    return e_n, e_x


collect_results = []
submissions = os.listdir(FILE_LOC)
for file_name in submissions:
    model = determine_model(file_name)
    scientist = determine_scientist(file_name, model)
    submitted_file = os.path.join(FILE_LOC, file_name)
    e_n, e_x = submission_results(submitted_file)

    collect_results.append(
        {
            'model': model,
            'scientist': scientist,
            'MSE E[N]': sum_e_n - e_n,
            'MSE E[X]': sum_e_x - e_x,
        }
    )


field_names = ['model', 'scientist', 'MSE E[N]', 'MSE E[X]']
with open('SubmissionAnswers.csv', 'w') as _file:
    writer = csv.DictWriter(_file, fieldnames=field_names)
    writer.writeheader()
    for result in collect_results:
        writer.writerow(result)
