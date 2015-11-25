#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import jp_parser
import codecs
import re
import time
from itertools import tee, izip, ifilter

"""
目前已經有斷好詞，並轉換成wordid的documents
現在要讀取每一個slide對應到documents的哪幾句，以slide為單位切



"""

def GetBrokenTxtNameList(path):
    ls_cmd = 'ls ' + path

    sa_txt_files = os.popen(ls_cmd).read()
    sa_txt_files = sa_txt_files.split('\n')

    del sa_txt_files[-1]

    return sa_txt_files
#end GetFileNameList()


def GetAlignFileNameList(path):
    ls_cmd = 'ls ' + path

    doc_dirs_name = os.popen(ls_cmd).read()
    doc_dirs_name = doc_dirs_name.split('\n')

    del doc_dirs_name[-1]

    # Concate '.sa.txt' after the list of directory names
    sa_ali_files = [s + '.align' for s in doc_dirs_name]

    return doc_dirs_name, sa_ali_files
#end GetAlignFileNameList()


def AppearInDict(token, token_id_dictionary):
#檢查token是否出現在token_id_dictionary，有的話回傳index；否則回傳－1
    for dic_index in range(0, len(token_id_dictionary)) :
        if token_id_dictionary[dic_index] == token:
            return dic_index
    #end for all tokens in dict
    return -1
#end AppearInDict()


def CreateWordIdDictionary(tokens_list, token_id_dictionary):
#需自動檢查該token是否出現在字典中，並回傳轉換成id的token list
    token_to_id_list = []
    for token in tokens_list:
        if len(token) > 0 and token != '(' and token != ')' and token != ';' and token != '-':

            index_of_token_in_dict = AppearInDict(token, token_id_dictionary)

            if index_of_token_in_dict != -1: #目前的token，詞典裡也有
                token_to_id_list.append(index_of_token_in_dict)

            #end if this token in dict
            else : # 目前的token不在詞典裡, 加入詞典並回傳index
                token_id_dictionary.append(token)
                token_to_id_list.append(len(token_id_dictionary))
            #end else not in dict
        #end if token is empty
    #end for
    return token_to_id_list
#end CreateWordIdDictionary()


def ReadThisFile(path_filename):
    fp = open(path_filename, 'r')

    full_txt_str = fp.read()

    #print full_txt_str
    splited_txt = full_txt_str.split('\n')
    return splited_txt
#end ReadThisFile()



def ReadAlignFormat(file_path_name) :
    fp = open(file_path_name, 'r').read()

    #格式：[('1', '0000'), ('2', '0008'), ('3', '0009'),
    #index就是slide的編號
    split_list = fp.split()
    split_list = filter(None, split_list)

    processed_list = []
    for element in split_list :
        if element[-1] == '+' :
            processed_list.append(int(element[0:len(element)-1]) + 1)
        elif element[-1] != '+' and len(element) == 4 :
            processed_list.append(element)
    #end for

    #processed_list = zip(processed_list[0::2], processed_list[1::2])
    #return structure like this : [('1', '0000'), ('2', '0008'), ('3', '0009'), ('4', '0016'), ('5', '0045'), ('6', '0055'), ('7', '0063'), ('8', '0093'), ('9', '0108'), ('10', '0108+'), ('11', '0147'), ('12', '0180'), ('13', '0192'), ('14', '0200'), ('15', '0207'), ('16', '0211'), ('17', '0230'), ('18', '0231'), ('19', '0257'), ('20', '0272'), ('21', '0289'), ('22', '0302'), ('23', '0310'), ('24', '0312'), ('25', '0326'), ('26', '0334'), ('27', '0334+'), ('28', '0346'), ('29', '0346+'), ('30', '0353'), ('31', '0353+'), ('32', '0364'), ('33', '0383'), ('34', '0397'), ('35', '0397+'), ('36', '0404')]

    return processed_list
#end ReadAlignFormat()


if __name__ == '__main__':

    # ------ Prepare sa.txt file names ------
    #path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/'
    doc_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/'
    wordid_docs_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/wid_PreprocessedDoc/'
    output_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/PreprocessedDoc/'


    doc_dir_names, align_file_names = GetAlignFileNameList(doc_path)
    word_id_txt_file_names = GetBrokenTxtNameList(wordid_docs_path)


    print len(align_file_names), align_file_names
    print len(word_id_txt_file_names), word_id_txt_file_names
    print len(doc_dir_names), doc_dir_names
    print '='*80

    sentence_line_num = ''
    token_id_dictionary = [] #index就是word id

    #align檔案格式：
    #slide數   句子編號
    #  1        0000
    #  2        0008
    #      ...
    # 10        0108+
    #      ...
    # 36        0404
    print doc_path + doc_dir_names[0] + '/' +  align_file_names[0]

    test = 0
    slide_and_sentnum_tuple = ReadAlignFormat(doc_path + doc_dir_names[test] + '/' +  align_file_names[test])
    #slide, sent_num

    #slide_and_sentnum_tuple.reverse()
    print slide_and_sentnum_tuple
    distance_between_slides = []
    #先計算slide與slide之間所橫跨的句數
    for distance in range(1, len(slide_and_sentnum_tuple)):
        distance_between_slides.append(int(slide_and_sentnum_tuple[distance])-int(slide_and_sentnum_tuple[distance-1]))
    #end for slide與slide之間所橫跨的句數

    print distance_between_slides

    print output_path + str(1) + '#' + doc_dir_names[0] + '.sa.txt'
    # 讀取已經斷好詞and轉換好word－id的檔案

    #開始斷句及寫入檔案：utf8格式
    for this_dir in doc_dir_names:
        wid_fp = open(wordid_docs_path + this_dir + '.sa.txt', 'r')
        wid_full_text = wid_fp.read()

        wid_list_splited = wid_full_text.split('\n')

        slide_and_sentnum_tuple = ReadAlignFormat(doc_path + this_dir + '/' +  this_dir + '.align')

        distance_between_slides = []

        #先計算slide與slide之間所橫跨的句數
        for distance in range(1, len(slide_and_sentnum_tuple)):
            distance_between_slides.append(int(slide_and_sentnum_tuple[distance])-int(slide_and_sentnum_tuple[distance-1]))
        #end for slide與slide之間所橫跨的句數

        slide_num = 1
        distance_index = 0

        slide_wid_fp = open(output_path + this_dir + '.' + '#' + str(slide_num) + '.txt', 'w')

        for line_num in range(0, len(wid_list_splited)) :
            a = 1
            if slide_num < len(slide_and_sentnum_tuple) :
                # 如果目前句子編號 < 差距 ； 那就直接寫入檔案
                if line_num < int(slide_and_sentnum_tuple[slide_num]):
                    slide_wid_fp.write(wid_list_splited[line_num])
                    slide_wid_fp.write('\n')
                #end if 目前句子編號 < 下一個slide開始的句子編號
                # 如果目前句子編號 >= 差距 ； 表示下一個slide開始了
                elif line_num == int(slide_and_sentnum_tuple[slide_num]):
                    slide_num = slide_num + 1
                    distance_index = distance_index + 1
                    slide_wid_fp.close()
                    slide_wid_fp = open(output_path + this_dir + '.' + '#' + str(slide_num) + '.txt', 'w')

                    slide_wid_fp.write(wid_list_splited[line_num])
                    slide_wid_fp.write('\n')
                #end if 目前句子編號 >= 下一個slide開始的句子編號
            #endif slide_num < len(slide_and_sentnum_tuple)
            else :
                # 如果目前句子編號 < 差距 ； 那就直接寫入檔案
                if line_num < len(slide_and_sentnum_tuple) :
                    slide_wid_fp.write(wid_list_splited[line_num])
                    slide_wid_fp.write('\n')
                #end if 目前句子編號 < 下一個slide開始的句子編號
                # 如果目前句子編號 >= 差距 ； 表示下一個slide開始了
                elif line_num == len(slide_and_sentnum_tuple) :
                    slide_num = slide_num + 1
                    distance_index = distance_index + 1
                    slide_wid_fp.close()
                    slide_wid_fp = open(output_path + this_dir + '.' + '#' + str(slide_num) + '.txt', 'w')

                    slide_wid_fp.write(wid_list_splited[line_num])
                    slide_wid_fp.write('\n')
                #end if 目前句子編號 >= 下一個slide開始的句子編號
            #end else achieve maximum slide numbers
        #end for lines in wid txt



        wid_fp.close()

    #end for


#end if __name__ == '__main__'