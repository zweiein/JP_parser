#! /usr/bin/env python
# -*- coding: utf-8 -*-



import CaboCha

def JpParser(target_sentence) :
#return tokenized word
    c = CaboCha.Parser()
    tree =  c.parse(target_sentence)

    #tree.toString(CaboCha.FORMAT_TREE)        # simple tree
    full_tree_string =  tree.toString(CaboCha.FORMAT_LATTICE)

    """
    # 樹的格式長這樣：
    --------------------
      * 0 6D 0/1 -2.457381
      太郎  名詞,固有名詞,人名,名,*,*,太郎,タロウ,タロー
      は 助詞,係助詞,*,*,*,*,は,ハ,ワ
      * 1 2D 0/0 1.509507
      この  連体詞,*,*,*,*,*,この,コノ,コノ
      * 2 4D 0/1 0.091699
      本 名詞,一般,*,*,*,*,本,ホン,ホン
      を 助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
      * 3 4D 1/2 2.359707
      二 名詞,数,*,*,*,*,二,ニ,ニ
      郎 名詞,一般,*,*,*,*,郎,ロウ,ロー
      を 助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
      * 4 5D 0/1 1.416783
      見 動詞,自立,*,*,一段,連用形,見る,ミ,ミ
      た 助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
      * 5 6D 0/1 -2.457381
      女性  名詞,一般,*,*,*,*,女性,ジョセイ,ジョセイ
      に 助詞,格助詞,一般,*,*,*,に,ニ,ニ
      * 6 -1D 0/1 0.000000
      渡し  動詞,自立,*,*,五段・サ行,連用形,渡す,ワタシ,ワタシ
      た 助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
      。 記号,句点,*,*,*,*,。,。,。
      EOS
    --------------------
    """

    splited_tree_list = full_tree_string.split('\n')

    if len(splited_tree_list[-1]) == 0 :
        del splited_tree_list[-1]
    # end if the last element is empty

    del_list = []


    #過濾開頭就是＊的，刪除掉

    for i in range(0, len(splited_tree_list)) :
        if '*' in splited_tree_list[i][0]  or len(splited_tree_list[i]) == 0:
            del_list.append(i)
    #end for walk around all split list

    for del_index in reversed(del_list) :
        del splited_tree_list[del_index]
    #end delete *


    # 再來只抓出第一個tab以前的字串
    tokenized_list = []

    for element in splited_tree_list:
        tab_index = 0

        for i in range(0, len(element)):
            if element[i] == '\t':
                tab_index = i
            #end if get tab index
        #end for walk this line string

        tokenized_list.append(element[0:tab_index])
    #for all filtered split tree list

    return tokenized_list
#end JpParser()



if __name__ == '__main__':
    sentence = '太郎はこの本を二郎を見た女性に渡した。'
    splitted_token_list = JpParser(sentence)


    for i in splitted_token_list :
        print i

#end if __name__ == '__main__'

