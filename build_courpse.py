import csv
import sys
import os
import json
from collections import defaultdict
import argparse

uid_to_text = defaultdict(list)



if len(sys.argv) != 2:
    if sys.argv[1] != ("train" or "test"):
        print("Please specify test or train data")
        sys.exit(1)



directory = '{}/documents/'.format(sys.argv[1])
out_file_name = "{}/{}.dat".format(sys.argv[1], sys.argv[1])
out_meta_file_name = '{}/metadata.dat'.format(sys.argv[1])






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



# Write data
with open(out_file_name, 'w+') as out_file:
    for uid in uid_to_text:
        for val in uid_to_text[uid]:
         out_file.write(val.get('title', 'None') + '\t' + val.get('abstract', 'None')  + '\n')

# Write Meta Data
with open(out_meta_file_name, 'w+') as meta_file:
    for uid in uid_to_text:
        for val in uid_to_text[uid]:
             meta_file.write(uid + "\n")
        #  meta_file.write(uid + '\t' + val.get('title', 'None') + '\t' + val.get('abstract', 'None')  + '\t' + ' '.join(val.get('introduction','None')) + '\n')