import os
import sys
import subprocess
import json

import MeCab
import jaconv
from kanjize import int2kanji, kanji2int

class JuliusDictGenerator:

    def __init__(self, path=None, output_file_name=None):
        self.read_config_file('./config.json')
        self.path = path if not path is None else self.config['output_path']
        self.output_file_name = output_file_name if not output_file_name is None else self.config['output_dict_name']
        self.output_file_path = self.path + '/' + self.output_file_name
        self.create_output_dir()

        
    def read_config_file(self, config_file_name):
        with open(config_file_name, mode='r') as conf_file:
            self.config = json.load(conf_file)

        self.yomi2voca_file_path = self.config['yomi2voca']
        self.mkdfa_file_path = self.config['mkdfa']
        self.number_range = self.config['number_range']
            

    def create_output_dir(self):
        os.makedirs(self.path, exist_ok=True)

        
    def generate_yomi_file(self):
        mecab = MeCab.Tagger('-Ochasen')
        existing_word_list = []

        with open(self.output_file_path + '.yomi', 'w') as yomi_file:
            with open(self.output_file_path + '.list', 'r') as list_file:
                
                for sentence in list_file:
                    words = mecab.parse(sentence).split('\n')

                    for word in words:
                        word_details = word.split('\t')
                    
                        # すでに存在している単語はスキップ
                        if word_details[0] in existing_word_list:
                            continue

                        # 文末(EOS) 以外の場合yomiファイルに記載
                        elif not word_details[0] == 'EOS' and not word_details[0] in existing_word_list:
                            output_line = word_details[0] + ' ' + jaconv.kata2hira(word_details[1]) + '\n'
                            existing_word_list.append(word_details[0])
                            yomi_file.write(output_line)

                        # 文末(EOS)の場合、文の書き出しを終了
                        else:
                            break

    # %n を含む文章を漢数字に置き換え, listファイルに書き出し
    def replace_number(self, sentenses_list):
        sentenses_list_str = ''

        for sentence in sentenses_list:
            if '%n' in sentence:
                for i in range(1,int(self.config['number_range'])):
                    sentenses_list_str += sentence.replace('%n', int2kanji(i)) + '\n'
            else:
                sentenses_list_str += sentence + '\n'
                
            with open(self.output_file_path + '.list', 'w') as list_file :
                list_file.write(sentenses_list_str)


    def generate_phone_file(self):
        # 実行コマンド
        command_conv_eucjp = 'iconv -f utf8 -t eucjp ' + self.output_file_path + '.yomi'
        command_yomi2voca = self.yomi2voca_file_path
        command_conv_utf8 = 'iconv -f eucjp -t utf8'

        # コマンド実行
        result_conv_eucjp = subprocess.Popen(command_conv_eucjp.split(' '), stdout=subprocess.PIPE)
        result_yomi2voca = subprocess.Popen(command_yomi2voca.split(' '), stdin=result_conv_eucjp.stdout,stdout=subprocess.PIPE)
        result_conv_utf8 = subprocess.check_output(command_conv_utf8.split(' '), stdin=result_yomi2voca.stdout)

        # phoneファイル書き出し
        with open(self.output_file_path + '.phone','wb') as phone_file:
            phone_file.write(result_conv_utf8)

            
    def generate_voca_file(self):

        END_VALUE = '% NS_B\n[s]\tsilB\n% NS_E\n[/s]\tsilE\n'
        voca_value = ''
        title_value = 'WORD'
        index = 0
        title_value_map = {}

        # phoneファイル読み込み & 整形
        with open(self.output_file_path + '.phone', 'r', encoding='UTF-8') as phone_file:
            for phone_line in phone_file:
                voca_value += '% ' + title_value + str(index) + '\n' + phone_line
                title_value_map[phone_line.split('\t')[0]] = title_value + str(index)
                index += 1
                
        voca_value += END_VALUE

        # vocaファイル書き出し
        with open(self.output_file_path + '.voca', 'w', encoding='UTF-8') as voca_file:
            voca_file.write(voca_value)

        return title_value_map

    
    def generate_grammar_file(self, title_value_map):

        INITIAL_SENTENCE = 'S : NS_B WORD NS_E\n'
        mecab = MeCab.Tagger('-Ochasen')

        grammar_result = INITIAL_SENTENCE

        # listファイルから文法整形
        with open(self.output_file_path + '.list', 'r', encoding='UTF-8') as list_file:
        
            for sentence in list_file:
                sentence_line = 'WORD :'
                words = mecab.parse(sentence).split('\n')
                for word in words:

                    word_details = word.split('\t')

                    if not word_details[0] == 'EOS' and not word_details[0] == '' :
                        sentence_line += ' ' + title_value_map[word_details[0]]
                grammar_result += sentence_line + '\n'


        # grammarファイル書き出し
        with open(self.output_file_path + '.grammar', 'w', encoding='UTF-8') as grammar_file:
            grammar_file.write(grammar_result)


    def generate_dict_file(self):
        command = self.mkdfa_file_path + ' ' + self.output_file_path
        result = subprocess.check_output(command.split(' '))

        
    def start(self, sentenses_list):
        self.replace_number(sentenses_list)
        self.generate_yomi_file()
        self.generate_phone_file()
        title_value_map = self.generate_voca_file()
        self.generate_grammar_file(title_value_map)
        self.generate_dict_file()
        

if __name__ == '__main__':
    sentenses_list = ["サンプル文言",
                      "エアコンの温度を下げて",
                      "エアコンつけて",
                      "電気つけて",
                      "テレビ消して",
                      "パソコンの調子が悪いです",
                      "暖房つけて",
                      "暖房切って",
                      "部屋が暑い",
                      "部屋が寒い",
                      "エアコン%n度",
                      "暖房%n度",
                      "暖房%n"
                      
    ]

    jdg = JuliusDictGenerator()
    jdg.start(sentenses_list)
