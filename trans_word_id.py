#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import jp_parser
import codecs
import re
import time

"""

讀取此路徑下的所有07-01.sa.txt （日期.sa.txt）
根據斷句的結果產生word_id的對應表

"""

def GetBrokenTxtNameList(path):
    ls_cmd = 'ls ' + path

    sa_txt_files = os.popen(ls_cmd).read()
    sa_txt_files = sa_txt_files.split('\n')

    del sa_txt_files[-1]

    return sa_txt_files
#end GetFileNameList()



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


if __name__ == '__main__':

    # ------ Prepare sa.txt file names ------
    #path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/'
    brokened_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/JP_PreprocessedDoc/'
    output_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/PreprocessedDoc/'
    sa_txt_file_names = GetBrokenTxtNameList(brokened_path)

    print sa_txt_file_names
    print len(sa_txt_file_names)
    print '='*80

    sentence_line_num = ''
    token_id_dictionary = [] #index就是word id

    sa_txt_file_names = reversed(sa_txt_file_names)
    #sa_txt_file_names = sa_txt_file_names[20:len(sa_txt_file_names)]
    #dir_names = dir_names[20:len(dir_names)]

    # 讀取已經斷好詞的檔案，建立詞典，並將它轉換成word id的檔案

    #開始斷句及寫入檔案：utf8格式
    for this_doc in sa_txt_file_names:
        #目前讀入了一篇文章，先用換行符號把文章切成句子
        split_doc_to_sentences_by_enter = ReadThisFile(brokened_path + this_doc)
        wp = open(output_path+this_doc, 'w')

        for this_sentence in split_doc_to_sentences_by_enter:
            #句子編號額外拿出來，不參與斷句；如果這個句子莫名其妙連編號也沒有，就不玩了
            if len(this_sentence) > 4:
                sentence_line_num = this_sentence[0:5]
            else :
                break

            #把“目前這個doc中的目前這一句”，除了句子編號的部分拿出來
            length = len(this_sentence)
            actual_sentence = this_sentence[6:length]

            # 剩下的部分已經斷好詞了，用空白切開拿去產生詞典即可
            finished_broken_sentence = actual_sentence.split()

            #TODO: 將斷詞結果轉換成word id，並產生“word id的對照文件”及產生“以word id取代日文的document檔”；//還要提供word id to日文字的function
            # CreateWordIdDictionary(tokens_list, token_id_dictionary) #需自動檢查該token是否出現在字典中，並回傳轉換成id的token list
            finished_broken_sentence_to_word_id = CreateWordIdDictionary(finished_broken_sentence, token_id_dictionary)

            wp.write(sentence_line_num)
            wp.write(' ')

            for tokens in finished_broken_sentence_to_word_id:
                wp.write(str(tokens))
                wp.write(' ')
            #end for tokens

            wp.write('\n')
        #end for sentences
        wp.close()

    #end for files

    wp = open(output_path+'word_id_list.txt', 'w')

    for i in range(0, len(token_id_dictionary)):
        wp.write(str(i) + '\t' + token_id_dictionary[i] )
        wp.write('\n')
    #end for
    wp.close()

#end if __name__ == '__main__'