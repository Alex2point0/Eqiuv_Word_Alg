import pandas as pd
import string
import operator
import re
from collections import Counter
import itertools
from collections import defaultdict
from itertools import combinations # Hint!

def make_itemsets(list_keywords):
    itemsets = [set(item) for item in list_keywords]
    return itemsets

def update_pair_counts(pair_counts, itemset):
    for a,b in combinations(itemset,2):
        counta = 0
        countb = 0
        # If word a is of less length than word b
        # and word a and word b shares the same first character
        # and also shares 2 more characters

        if len(a) < len(b) and a[0] == b[0]:
            for letter in a:
                if letter in b:
                    counta += 1
            if counta >= 3:
                pair_counts[(a, b)] += 1


        # If word b is of less length than word a
        # and word a and word b shares the same first character
        # and also shares 2 more characters

        if len(b) < len(a) and b[0] == a[0]:
            for letter in b:
                if letter in a:
                    countb += 1
            if countb >= 3:
                pair_counts[(b, a)] += 1

    return pair_counts

def update_item_counts(item_counts, itemset):
    # for each word or item in the keyword set increase that word or item count by 1
    for a in itemset:
        item_counts[a] += 1
    return item_counts

def filter_rules_by_conf (pair_counts, item_counts, threshold, MIN_COUNT):
    rules = {} # (item_a, item_b) -> conf (item_a => item_b)

    for (a, b) in pair_counts:
        conf = pair_counts[(a, b)]/item_counts[a]
        if conf >= threshold and item_counts[a] >= MIN_COUNT:
            rules[(a, b)] = (conf, pair_counts[(a, b)], item_counts[a])

    return rules

def find_assoc_rules(set_keywords, threshold, MIN_COUNT):

    # Use defaultdict to start a dictionary for pair counts and item counts
    pair_counts = defaultdict(int)
    item_counts = defaultdict(int)

    # for each item in the set of keywords we will make a pair count and an item count
    for itemset in set_keywords:
        pair_c = update_pair_counts(pair_counts, itemset)
        item_c = update_item_counts(item_counts, itemset)

    rules = filter_rules_by_conf(pair_c, item_c, threshold, MIN_COUNT)
    return rules

def col_str(list_cols, dataf):

    # makes the columns in the list_cols to string type.
    for i in list_cols:
        dataf[i] = dataf[i].astype(str)
    return dataf

def desc_sep(row, cols_adjust):

    # Preprocessing before running algorithm focuses on the keyword portion of each part description(before the comma):
    # Separate out words before the comma in each column and puts them together in a list
    # If there is no commas and it is one word with no space then that word is put in to the list, else it is not
    # Turns that list of words in to a set, in order to not get repeats, then turns it back in to a list.

    keys = []
    for headers in cols_adjust:
        desc = row[headers]
        if ',' in desc:
            key_inst = desc.split(',', 1)[0]
            keys.extend(key_inst.split(' '))

        elif ((' ' in desc) == False) and desc != '':
            keys.append(desc)

    # uses sets to make the keywords list unique
    keywords = list(filter(None, keys))
    keywords = set(keywords)
    keyword = list(keywords)
    return keyword

def keyword_count(row):
    return len(row['Word_Grouping'])

# putting part info data in to a dataframe with pandas
part_info = pd.read_csv('Part_descriptions.csv', encoding='UTF-8')

# cols_adjust is a list of columns that will be worked on.
cols_adjust = ['plm_part_desc_txt',
            'plm_part_desc_short_txt', 'bdw_desc_txt',
            'spares_nomen_txt', 'spares_keyword_txt']

# inital preprocessing of the columns in cols_adjust, making them a string type, and replacing null with ' '
part_info = part_info.where((pd.notnull(part_info)), ' ')
part_info = col_str(cols_adjust, part_info)
part_info = part_info.replace('nan', ' ')

# Making Word_Grouping and Word_Grouping_Count with the functions below.
part_info['Word_Grouping'] = part_info.apply(desc_sep, cols_adjust = cols_adjust, axis=1)
part_info['Word_Grouping_Count'] = part_info.apply(keyword_count, axis=1)

# keep the rows with Word_Grouping_Count greater than 1
part_info_filtered = part_info[part_info['Word_Grouping_Count'] > 1]

# start the pairwise algorithm by making sets of from the column Word_Grouping
list_keywords = part_info_filtered['Word_Grouping'].tolist()
set_keywords = make_itemsets(list_keywords)

# Confidence threshold
THRESHOLD = 0.9
# Only consider rules for items appearing at least `MIN_COUNT` times.
MIN_COUNT = 5

# start the pairwise algorithm with the set of keywords, threshold and min count
rules = find_assoc_rules(set_keywords, THRESHOLD, MIN_COUNT)
print('THRESHOLD', THRESHOLD)
print('MIN_COUNT', MIN_COUNT)
print(len(rules))

equiv_word = []
target_word = []
confidence = []
pair_cts = []
item_cts = []

# Summarizing the results in to a dataframe.
for key, value in rules.items():
    equiv_word.append(key[0])
    target_word.append(key[1])
    confidence.append(value[0])
    pair_cts.append(value[1])
    item_cts.append(value[2])

rules_df = [('equiv_word', equiv_word),
            ('target_word', target_word),
            ('confidence', confidence),
            ('pair_cts', pair_cts),
            ('item_cts', item_cts)]

rules_df = pd.DataFrame.from_items(rules_df)
rules_df.to_csv('Equiv_Words.csv', encoding='cp1252')

print('done')
