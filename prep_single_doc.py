#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import jp_parser
import re

"""
/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/07-01
/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/07-02
.
.
.
/Volumes/disk1/NTCIR/SDPWS1to7/NTCIR12-SpokenQueryDoc2/NTCIR12-SpokenQueryDoc2/Document/13-11

讀取此路徑下的所有07-01.sa.txt （日期.sa.txt）
處理後產生新的日期.sa.txt

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

    '''
    # 先拿掉utterancce編號, [0:5]是編號  // 0001: (s2)まず背景ですが(F...
    #                                    ^^^^^
    length = len(this_sentence)
    this_sentence = this_sentence[6:length]
    '''
    # 保留行號
    print '@', this_sentence

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
        if this_sentence[walk] == '(' and this_sentence[walk+1] == 'F' :
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
           (this_sentence[walk] == '(' and this_sentence[walk+1] == '?' ) or \
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

        #print '  #', this_sentence
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
    #dir_names, sa_txt_file_names = GetFileNameList(path)

    #print sa_txt_file_names
    #print '='*80

    #splited_tokens_by_enter = ReadThisFile(path+dir_names[0]+'/'+sa_txt_file_names[0])

    #print len(splited_tokens_by_enter)
    #print splited_tokens_by_enter

    #splited_tokens_by_enter = ReadThisFile(path+'07-19'+'/'+'07-19.sa.txt')

    #print len(splited_tokens_by_enter)
    #print splited_tokens_by_enter

    #print FilterSpecialToken(splited_tokens_by_enter[239])
    #(F え)デコーダは(F ま)(A (W ジュリアス;ジュリウス);Ｊｕｌｉｕｓ)で(F えーと)音響モデルトライフォンで言語モデルは
    #デコーダはジュリウス;Ｊｕｌｉｕｓ)で音響モデルトライフォンで言語モデルは

    #processed_normal_sentences = FilterSpecialToken(splited_tokens_by_enter[8]) #397 45


    dir_names = ['07-01']
    sa_txt_file_names = [dir_names[0]+'.sa.txt']

    splited_tokens_by_enter = ReadThisFile(path+dir_names[0]+'/'+sa_txt_file_names[0])

    print path+dir_names[0]+'/'+sa_txt_file_names[0]


    for i in range(0, len(splited_tokens_by_enter)):
        wp = open(output_path+sa_txt_file_names[0], 'w')

        for this_sentence in range(0, len(sa_txt_file_names[0])):
            sentence_line_num = splited_tokens_by_enter[this_sentence][0:5]
            print sentence_line_num
            length = len(splited_tokens_by_enter[this_sentence])
            actual_sentence = splited_tokens_by_enter[this_sentence][6:length]

            processed_normal_sentence = FilterSpecialToken(actual_sentence)
            print '    ', processed_normal_sentence
            finished_broken_sentence = jp_parser.JpParser(processed_normal_sentence)

            #print '        ', finished_broken_sentence

            wp.write(sentence_line_num)
            wp.write(' ')

            for tokens in range(0, len(finished_broken_sentence)):
                wp.write(finished_broken_sentence[tokens])
                wp.write(' ')
            #end for tokens

            #print '!!! finish'
            wp.write('\n')
        #end for sentences
        wp.close()

    #(F え)デコーダは(F ま)(A (W ジュリアス;ジュリウス);Ｊｕｌｉｕｓ)で(F えーと)音響モデルトライフォンで言語モデルは
    #デコーダはジュリウス;Ｊｕｌｉｕｓ)で音響モデルトライフォンで言語モデルは

    #print FilterSpecialToken(splited_tokens_by_enter[276]) #397 45



    '''
    for element in  splited_tokens:
        temp_token_list = jp_parser.JpParser(element)
        for i in range(0, len(temp_token_list)):
            print temp_token_list[i]

    #for name in sa_txt_file_names:
    '''

    #    break
    #end for all filenames




#end if __name__ == '__main__'