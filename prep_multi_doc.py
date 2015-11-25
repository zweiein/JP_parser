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
斷句處理後產生新的日期.sa.txt

"""

def GetFileNameList(path):
    ls_cmd = 'ls ' + path

    doc_dirs_name = os.popen(ls_cmd).read()
    doc_dirs_name = doc_dirs_name.split('\n')

    del doc_dirs_name[-1]

    # Concate '.sa.txt' after the list of directory names
    sa_txt_files = [s + '.sa.txt' for s in doc_dirs_name]

    return doc_dirs_name, sa_txt_files
#end GetFileNameList()


def FilterSpecialToken(this_sentence):
#1) 尖括號夾起來的直接濾掉
#2) 根據小括號裏面的內容決定要濾掉還是留下重要資訊
#3) 還有utterance編號也要濾掉；這行如果只有編號跟尖括號就拿掉
#4) 特殊格式：
#             狀態？     (s1)                                => 可省略
#             語助詞     (F えー)                             => 可省略
#             ?         (?)                                 => 可省略
#             外來語     (A イーラーニング;ｅ−ｌｅａｒｎｉｎｇ)    => 保留後面的    ｅ−ｌｅａｒｎｉｎｇ
#    (語者有講)省略語？    (D そし)                             => 保留後面的    そし
#           漢字拼音     (W ジギョウ;授業)                      => 保留後面的    授業
#           背景雜音     <VAD誤り>                             => 可省略

#5) 注意的一點：並排的巢狀的case沒有完全考慮到！
#                  (A (W XX;XX);XX) => 有
#                  (A (W XX;XX);XX  (W XX;XX)) => 應該沒有


    '''
    # 先拿掉utterancce編號, [0:5]是編號  // 0001: (s2)まず背景ですが(F...
    #                                    ^^^^^
    length = len(this_sentence)
    this_sentence = this_sentence[6:length]
    '''
    # 保留行號
    #print this_sentence

    #先用regular expression濾掉 (s1), (s2), ...
    #this_sentence =  re.sub('\(s\d\)', '', this_sentence)
    #print 'sub (s) //  ', re.sub('\(s\d\)', '', this_sentence)
    #print 'regex: ', this_sentence

    parentheses_pairs = []
    greater_less_pairs = []

    replaced_pairs = []

    last_left_xiaoguahao = -1
    last_left_xiaoyu = -1

    ##print len(this_sentence)

    label_D_str = []
    walk = 0 #實際上在使用的index


    #regular expression 似乎不能濾掉日文字... 只好用parse的
    for i in range(0, len(this_sentence)):
        if walk == len(this_sentence):
            break

        # '(s數字)'的直接濾掉無所謂
        if this_sentence[walk] == '(' and this_sentence[walk+1] == 's' :
            last_left_xiaoguahao = walk

            for c in range(walk, len(this_sentence)):
                if this_sentence[c] != ')':
                    label_D_str.append(this_sentence[c])
                else:
                    label_D_str = []
                    replaced_pairs.append((walk, c, 'F', label_D_str))
                    walk = c
                    break
        #end if get '(s'


        # '(F XXX)'的直接濾掉無所謂
        if ( this_sentence[walk] == '(' and this_sentence[walk+1] == 'F' )  or \
           ( this_sentence[walk] == '(' and this_sentence[walk+1] == '?' and this_sentence[walk+2] == ')'):
            last_left_xiaoguahao = walk

            for c in range(walk, len(this_sentence)):
                if this_sentence[c] != ')':
                    label_D_str.append(this_sentence[c])
                else:
                    label_D_str = []
                    replaced_pairs.append((walk, c, 'F', label_D_str))
                    break
            #end for
        #end if get '(F'


        # '(D XXX)'的話，要保留XXX的部分
        if (this_sentence[walk] == '(' and this_sentence[walk+1] == 'D' ) or \
           (this_sentence[walk] == '(' and this_sentence[walk+1] == '?' and this_sentence[walk+2] != ')' ) or \
           (this_sentence[walk] == '(' and this_sentence[walk+1] == 'N' ) :
            last_left_xiaoguahao = walk

            #read until get the next ')'
            for c in range(walk, len(this_sentence)):
                if this_sentence[c] != ')':
                    label_D_str.append(this_sentence[c])
                else:
                    label_D_str = ''.join(label_D_str)
                    split_label_D = label_D_str.split()

                    label_D_str = split_label_D[-1]

                    replaced_pairs.append((walk, c, 'D', label_D_str))
                    label_D_str = []
                    last_left_xiaoguahao = -1
                    walk = c
                    break
            #end for
        #end if

        # '(A OOO;XXX)'的話，要保留XXX的部分
        if ( this_sentence[walk] == '(' and this_sentence[walk+1] == 'A' ) or \
             this_sentence[walk] == '(' and this_sentence[walk+1] == 'W' :
            last_left_xiaoguahao = walk
            guahao_num_in_substr = 0

            #read until get the next ')'
            for c in range(walk, len(this_sentence)):
                if this_sentence[c] == '(' :
                    #label_D_str.append(this_sentence[c])
                    guahao_num_in_substr = guahao_num_in_substr + 1
                #end if

                if this_sentence[c] != ')'  :
                    label_D_str.append(this_sentence[c])


                if this_sentence[c] == ')' and guahao_num_in_substr != 0 :
                    label_D_str.append(this_sentence[c])
                    guahao_num_in_substr = guahao_num_in_substr - 1


                if this_sentence[c] == ')' and guahao_num_in_substr == 0 :
                    label_D_str = ''.join(label_D_str)
                    split_label_D = label_D_str.split(';')
                    label_D_str = split_label_D[-1]
                    label_D_str = label_D_str[0:len(label_D_str)-1]

                    replaced_pairs.append((walk, c, 'D', label_D_str))

                    label_D_str = []
                    last_left_xiaoguahao = -1
                    walk = c
                    break
            #end for
        #end if

        if this_sentence[walk] == '<':
            last_left_xiaoyu = walk
        #end if get '<'

        if this_sentence[walk] == '>':
            replaced_pairs.append((last_left_xiaoyu, walk, '<', label_D_str))
            last_left_xiaoyu = -1
        #end if '>'

        walk = walk + 1
    #end for

    #print this_sentence

    #print '='*80
    #print len(replaced_pairs)
    #print replaced_pairs

    rp_len = len(replaced_pairs)

    # 濾掉小括號
    for i in range(0, rp_len):
        start, end, label, target_str = replaced_pairs.pop()

        #print '----label= ', label, '| i= ', i

        if start != 0 :
            if label == 'F' or label == '<' :
                this_sentence = this_sentence[0:start] + this_sentence[end+1:len(this_sentence)]

            if label == 'D' or label == 'A':
                #print '    (start, end)= (', start, ', ', end, ') |', this_sentence[0:start], '| target= ', target_str, '| end= ', this_sentence[end+1:len(this_sentence)]
                #print this_sentence[end:len(this_sentence)]
                this_sentence = this_sentence[0:start] + target_str + this_sentence[end+1:len(this_sentence)]
        #end if

        else:
            if label == 'F' or label == '<' :
                this_sentence = this_sentence[end+1:len(this_sentence)]

            if label == 'D' or label == 'A':
                this_sentence = target_str + this_sentence[end+1:len(this_sentence)]
        #end else

        ##print '  #', this_sentence
    #end for

    ##print '='*80
    return this_sentence
#end FilterSpecialToken()



def ReadThisFile(path_filename):
    fp = open(path_filename, 'r')

    full_txt_str = fp.read()

    #print full_txt_str
    splited_txt = full_txt_str.split('\n')
    return splited_txt
#end ReadThisFile()


if __name__ == '__main__':

    # ------ Prepare sa.txt file names ------
    path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/'
    output_path = '/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/PreprocessedDoc/'
    dir_names, sa_txt_file_names = GetFileNameList(path)

    print sa_txt_file_names
    print '='*80

    #sa_txt_file_names = ['07-04.sa.txt']
    #dir_names = ['07-04']

    sentence_line_num = ''

    #開始斷句及寫入檔案：utf8格式
    for this_doc in sa_txt_file_names:
        #目前讀入了一篇文章，先用換行符號把文章切成句子
        split_doc_to_sentences_by_enter = ReadThisFile(path + this_doc[0:5] + '/' + this_doc)
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

            #拿出來的未編號部分才是句子的本體，丟進去斷詞
            processed_normal_sentence = FilterSpecialToken(actual_sentence)
            finished_broken_sentence = jp_parser.JpParser(processed_normal_sentence)

            #wp.write(sentence_line_num)
            #wp.write(' ')

            for tokens in finished_broken_sentence:
                wp.write(tokens)
                wp.write(' ')
            #end for tokens

            wp.write('\n')
        #end for sentences
        wp.close()

    #end for files

#end if __name__ == '__main__'