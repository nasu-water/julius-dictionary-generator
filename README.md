# julius-dictionary-generator( jdg )

自作スマートスピーカを作成中に必要となったJuliusの辞書ファイルを自動作成したいと思いこのプログラムを作成しました。  
先人たちがすでにもっと効率の良いプログラムを開発していそうですが、ちょっとした追加機能がほしかったので自作しました。  
通常の文章の形態素解析を行い辞書に取り込むのはもちろん、スマートスピーカで使用する際によく使う数字を含んだ文章を自動生成する機能を追加しました。  
自分個人の使用、学習用途のため作成したもののため精度やその他の問題に対しての保証できません。  

## インストール

`pip3 install git+https://github.com/nasu-water/julius-dictionary-generator#egg=jdg`

## 使い方  

```python
from jdg import JuliusDictGenerator

yomi2voca = "/Your/Path/julius/julius-4.4.2.1/gramtools/yomi2voca/yomi2voca.pl"
mkdfa = "/Your/Path/julius/julius-4.4.2.1/gramtools/mkdfa/mkdfa.pl"
output_path = "./dict"
output_dict_name = "words"
number_range = 30

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
                  "エアコン%n度"
                  ]

jdg = JuliusDictGenerator(output_path, output_dict_name, yomi2voca, mkdfa, number_range)
jdg.start(sentenses_list)

```

文章内に`%n`と入っている場合、その箇所を数値化した文章を作成します。  
`%n`で作成される数値化した文章の数値の範囲は`config.json`の`number_range`で設定された値に沿います。  
`number_range`に`100`が設定されている場合、1〜99の数値範囲の文章を作成します。  

## 環境とソフトウェア
- Python 3.7.5
- julius 4.4.2.1
- MeCab 0.996
- Raspberry Pi 3 Model B+ / Raspbian 10
