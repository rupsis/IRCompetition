import csv
import os
import json
from collections import defaultdict

uid_to_text = defaultdict(list)

directory = 'train/documents/'

# open the file
with open('{}metadata.csv'.format(directory)) as f_in:
    counter = 0
    reader = csv.DictReader(f_in)
    for row in reader:
        
        # access some metadata
        uid = row['uid']
        title = row['title']
        abstract = row['abstract']
        authors = row['authors'].split('; ')

        # access the full text (if available) for Intro
        introduction = []
        if row['pdf_json_files']:
            for json_path in row['pdf_json_files'].split('; '):
                with open('{}{}'.format(directory,json_path)) as f_json:
                    full_text_dict = json.load(f_json)
                    
                    # grab introduction section from *some* version of the full text
                    for paragraph_dict in full_text_dict['body_text']:
                        paragraph_text = paragraph_dict['text']
                        section_name = paragraph_dict['section']
                        if 'intro' in section_name.lower():
                            introduction.append(paragraph_text)

                    # stop searching other copies of full text if already got introduction
                    if introduction:
                        break

        # save for later usage
        uid_to_text[uid].append({
            'title': title,
            'abstract': abstract,
            'introduction': introduction
        })

        #  build sample index
        counter += 1
        if counter >= 1000:
            break

with open('train/train.dat', 'w') as out_file:
    for uid in uid_to_text:
        for val in uid_to_text[uid]:
         out_file.write(uid + '\t' + val.get('title', 'None') + '\t' + val.get('abstract', 'None')  + '\t' + ' '.join(val.get('introduction','None')) + '\n')