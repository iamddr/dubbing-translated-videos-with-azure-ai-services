
startList = [1,2,3,4,5,6,7,8,9]
endList = [2,3,4,5,6,7,8,9,10]

starting_value = 0

endList.insert(0, starting_value)

zipObject = zip(startList, endList)

differences_list = [startList - endList for startList, endList in zipObject]
len(differences_list)

import json
import os

with open('sentences_list.json', 'r') as f:
    sentences_list = json.load(f)

sentences_list

sentences_list[0]['duration']
sentences_list[0]['actual_duration']


[(sentence['actual_duration'], sentence['duration']) for sentence in sentences_list]
[sentence['actual_duration'] - sentence['duration'] for sentence in sentences_list]

## Ignore statements that are SHORTER than the original duration.
sentences_to_adjust = [
    (sentence['actual_duration'], sentence['duration'], sentence['actual_duration'] - sentence['duration']) 
    for sentence in sentences_list if sentence['actual_duration'] > sentence['duration']
]

## Of the remaining statements, choose the one that is LONGEST difference. 
max_difference = max([sentence[2] for sentence in sentences_to_adjust])
adjustment_tuple = [sentence for sentence in sentences_to_adjust if sentence[2] == max_difference][0]

## Calculate the prosody rate based on the difference of the longest difference phrase. 
prosody_rate = adjustment_tuple[0]/adjustment_tuple[1]



### 
### Calculate breaks
### 
import json
import os
import xml
import xml.etree.ElementTree as etree
from pprint import pprint

with open('sentences_list.json', 'r') as f:
    sentences_list = json.load(f)

def generate_ssml_breaks(parent_xml, break_length_in_sec) -> xml.Element:
        max_break_length_in_sec = 5
        num_full_breaks = int(break_length_in_sec // max_break_length_in_sec)
        remainder_break_length_in_sec = break_length_in_sec % max_break_length_in_sec

        if num_full_breaks == 0:
            break_list = [remainder_break_length_in_sec]
        else:
            break_list = [5] * num_full_breaks
            if remainder_break_length_in_sec > 0:
                break_list.append(remainder_break_length_in_sec)

        for b in break_list:
            ## insert code to add a break here.
            brk_ms = int(b * 1000)
            brk = xml.Element("break", attrib={"time":f"{brk_ms}"})
            parent_xml.insert(0, brk)

for sentence in sentences_list:
## Insert the desired breaks into the SSML.
    phrase_ssml = sentence['ssml']
    root = etree.XML(phrase_ssml)
    tree = etree.ElementTree(root)
    etree.register_namespace("", "http://www.w3.org/2001/10/synthesis")
    prosody_tag = [tag for tag in root.iter('{http://www.w3.org/2001/10/synthesis}prosody')][0]
    break_element = etree.Element('break', attrib={'strength': 'YOURMOM'})
    prosody_tag.insert(0, break_element)
    prosody_tag.append(break_element)


import xml
from xml.etree import ElementTree

phrase_ssml = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xml:lang=\"en-Us\"><voice name=\"en-US-AriaNeural\"><prosody rate=\"1.5\"><s>Sounds unlikely. Thomas is what you're saying sounds like because it says selective methods and private endpoint. So yeah, which would be interesting. This will be. This will be good feedback for the product team. If that's the case, so you get the refresh here. We hit ohh it's not safe yet.</s><break strength=\"none\" /></prosody></voice></speak>"
root = ElementTree.XML(phrase_ssml)
ElementTree.register_namespace("", "http://www.w3.org/2001/10/synthesis")
prosody_tag = [tag for tag in root.iter('{http://www.w3.org/2001/10/synthesis}prosody')][0]

## Insert the breaks
max_break_length_in_sec = 5
break_length_in_sec = 9.247875
num_full_breaks = int(break_length_in_sec // max_break_length_in_sec)
remainder_break_length_in_sec = break_length_in_sec % max_break_length_in_sec

if num_full_breaks == 0:
    break_list = [remainder_break_length_in_sec]
else:
    break_list = [5] * num_full_breaks
    if remainder_break_length_in_sec > 0:
        break_list.append(remainder_break_length_in_sec)

for b in break_list:
    print(b)
    ## insert code to add a break here.
    brk_ms = int(b * 1000)
    brk = ElementTree.Element("break", attrib={"time":f"{brk_ms}"})
    prosody_tag.insert(0, brk)
    
ElementTree.tostring(root, encoding='unicode')     


