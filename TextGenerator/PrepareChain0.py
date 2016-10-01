# -*- coding: utf-8 -*-

u"""
与えられた文書からマルコフ連鎖のためのチェーン（連鎖）を作成して、DBに保存するファイル
"""

import unittest

import re
import MeCab
import sqlite3
from collections import defaultdict


class PrepareChain(object):
    u"""
    チェーンを作成してDBに保存するクラス
    """

    BEGIN = u"__BEGIN_SENTENCE__"
    END = u"__END_SENTENCE__"

    DB_PATH = "/Users/Macaria/Ebios/Rails/habomailang_api/TextGenerator/chain.db"
    DB_SCHEMA_PATH = "/Users/Macaria/Ebios/Rails/habomailang_api/TextGenerator/schema.sql"

    def __init__(self, text):
        u"""
        初期化メソッド
        @param text チェーンを生成するための文章
        """
        if isinstance(text, str):
            text = text.decode("utf-8")
        self.text = text

        # 形態素解析用タガー
        self.tagger = MeCab.Tagger('-Ochasen')

    def make_triplet_freqs(self):
        u"""
        形態素解析から3つ組の出現回数まで
        @return 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
        """
        # 長い文章をセンテンス毎に分割
        sentences = self._divide(self.text)

        # 3つ組の出現回数
        triplet_freqs = defaultdict(int)

        # センテンス毎に3つ組にする
        for sentence in sentences:
            # 形態素解析
            morphemes = self._morphological_analysis(sentence)
            # 3つ組をつくる
            triplets = self._make_triplet(morphemes)
            # 出現回数を加算
            for (triplet, n) in triplets.items():
                triplet_freqs[triplet] += n

        return triplet_freqs

    def _divide(self, text):
        u"""
        「。」や改行などで区切られた長い文章を一文ずつに分ける
        @param text 分割前の文章
        @return 一文ずつの配列
        """
        # 改行文字以外の分割文字（正規表現表記）
        delimiter = u"。|．|\."

        # 全ての分割文字を改行文字に置換（splitしたときに「。」などの情報を無くさないため）
        text = re.sub(ur"({0})".format(delimiter), r"\1\n", text)

        # 改行文字で分割
        sentences = text.splitlines()

        # 前後の空白文字を削除
        sentences = [sentence.strip() for sentence in sentences]

        return sentences

    def _morphological_analysis(self, sentence):
        u"""
        一文を形態素解析する
        @param sentence 一文
        @return 形態素で分割された配列
        """
        morphemes = []
        sentence = sentence.encode("utf-8")
        node = self.tagger.parseToNode(sentence)
        while node:
            if node.posid != 0:
                morpheme = node.surface.decode("utf-8")
                morphemes.append(morpheme)
            node = node.next
        return morphemes

    def _make_triplet(self, morphemes):
        u"""
        形態素解析で分割された配列を、形態素毎に3つ組にしてその出現回数を数える
        @param morphemes 形態素配列
        @return 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
        """
        # 3つ組をつくれない場合は終える
        if len(morphemes) < 3:
            return {}

        # 出現回数の辞書
        triplet_freqs = defaultdict(int)

        # 繰り返し
        for i in xrange(len(morphemes)-2):
            triplet = tuple(morphemes[i:i+3])
            triplet_freqs[triplet] += 1

        # beginを追加
        triplet = (PrepareChain.BEGIN, morphemes[0], morphemes[1])
        triplet_freqs[triplet] = 1

        # endを追加
        triplet = (morphemes[-2], morphemes[-1], PrepareChain.END)
        triplet_freqs[triplet] = 1

        return triplet_freqs

    def save(self, triplet_freqs, init=False):
        u"""
        3つ組毎に出現回数をDBに保存
        @param triplet_freqs 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
        """
        # DBオープン
        con = sqlite3.connect(PrepareChain.DB_PATH)

        # 初期化から始める場合
        if init:
            # DBの初期化
            with open(PrepareChain.DB_SCHEMA_PATH, "r") as f:
                schema = f.read()
                con.executescript(schema)

            # データ整形
            datas = [(triplet[0], triplet[1], triplet[2], freq) for (triplet, freq) in triplet_freqs.items()]

            # データ挿入
            p_statement = u"insert into chain_freqs (prefix1, prefix2, suffix, freq) values (?, ?, ?, ?)"
            con.executemany(p_statement, datas)

        # コミットしてクローズ
        con.commit()
        con.close()

    def show(self, triplet_freqs):
        u"""
        3つ組毎の出現回数を出力する
        @param triplet_freqs 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
        """
        for triplet in triplet_freqs:
            print "|".join(triplet), "\t", triplet_freqs[triplet]


class TestFunctions(unittest.TestCase):
    u"""
    テスト用クラス
    """

    def setUp(self):
        u"""
        テストが実行される前に実行される
        """
        self.text = u"こんにちは。　今日は、楽しい運動会です。hello world.我輩は猫である\n  名前はまだない。我輩は犬である\r\n名前は決まってるよ"
        self.chain = PrepareChain(self.text)

    def test_make_triplet_freqs(self):
        u"""
        全体のテスト
        """
        triplet_freqs = self.chain.make_triplet_freqs()
        answer = {(u"__BEGIN_SENTENCE__", u"今日", u"は"): 1, (u"今日", u"は", u"、"): 1, (u"は", u"、", u"楽しい"): 1, (u"、", u"楽しい", u"運動会"): 1, (u"楽しい", u"運動会", u"です"): 1, (u"運動会", u"です", u"。"): 1, (u"です", u"。", u"__END_SENTENCE__"): 1, (u"__BEGIN_SENTENCE__", u"hello", u"world"): 1, (u"hello", u"world", u"."): 1, (u"world", u".", u"__END_SENTENCE__"): 1, (u"__BEGIN_SENTENCE__", u"我輩", u"は"): 2, (u"我輩", u"は", u"猫"): 1, (u"は", u"猫", u"で"): 1, (u"猫", u"で", u"ある"): 1, (u"で", u"ある", u"__END_SENTENCE__"): 2, (u"__BEGIN_SENTENCE__", u"名前", u"は"): 2, (u"名前", u"は", u"まだ"): 1, (u"は", u"まだ", u"ない"): 1, (u"まだ", u"ない", u"。"): 1, (u"ない", u"。", u"__END_SENTENCE__"): 1, (u"我輩", u"は", u"犬"): 1, (u"は", u"犬", u"で"): 1, (u"犬", u"で", u"ある"): 1, (u"名前", u"は", u"決まっ"): 1, (u"は", u"決まっ", u"てる"): 1, (u"決まっ", u"てる", u"よ"): 1, (u"てる", u"よ", u"__END_SENTENCE__"): 1}
        self.assertEqual(triplet_freqs, answer)

    def test_divide(self):
        u"""
        一文ずつに分割するテスト
        """
        sentences = self.chain._divide(self.text)
        answer = [u"こんにちは。", u"今日は、楽しい運動会です。", u"hello world.", u"我輩は猫である", u"名前はまだない。", u"我輩は犬である", u"名前は決まってるよ"]
        self.assertEqual(sentences.sort(), answer.sort())

    def test_morphological_analysis(self):
        u"""
        形態素解析用のテスト
        """
        sentence = u"今日は、楽しい運動会です。"
        morphemes = self.chain._morphological_analysis(sentence)
        answer = [u"今日", u"は", u"、", u"楽しい", u"運動会", u"です", u"。"]
        self.assertEqual(morphemes.sort(), answer.sort())

    def test_make_triplet(self):
        u"""
        形態素毎に3つ組にしてその出現回数を数えるテスト
        """
        morphemes = [u"今日", u"は", u"、", u"楽しい", u"運動会", u"です", u"。"]
        triplet_freqs = self.chain._make_triplet(morphemes)
        answer = {(u"__BEGIN_SENTENCE__", u"今日", u"は"): 1, (u"今日", u"は", u"、"): 1, (u"は", u"、", u"楽しい"): 1, (u"、", u"楽しい", u"運動会"): 1, (u"楽しい", u"運動会", u"です"): 1, (u"運動会", u"です", u"。"): 1, (u"です", u"。", u"__END_SENTENCE__"): 1}
        self.assertEqual(triplet_freqs, answer)

    def test_make_triplet_too_short(self):
        u"""
        形態素毎に3つ組にしてその出現回数を数えるテスト
        ただし、形態素が少なすぎる場合
        """
        morphemes = [u"こんにちは", u"。"]
        triplet_freqs = self.chain._make_triplet(morphemes)
        answer = {}
        self.assertEqual(triplet_freqs, answer)

    def test_make_triplet_3morphemes(self):
        u"""
        形態素毎に3つ組にしてその出現回数を数えるテスト
        ただし、形態素がちょうど3つの場合
        """
        morphemes = [u"hello", u"world", u"."]
        triplet_freqs = self.chain._make_triplet(morphemes)
        answer = {(u"__BEGIN_SENTENCE__", u"hello", u"world"): 1, (u"hello", u"world", u"."): 1, (u"world", u".", u"__END_SENTENCE__"): 1}
        self.assertEqual(triplet_freqs, answer)

    def tearDown(self):
        u"""
        テストが実行された後に実行される
        """
        pass


if __name__ == '__main__':
    # unittest.main()

    text = u"""少しムチとした食感のもの。
カタメすぎる仕上がり。
プルプルすぎる食感のもの。
柔らかめすぎる仕上がり。
ズババと啜れちゃう物足りないもの。
汁染みすぎた仕上がり。
クニュクニュすぎる食感のもの。
ウマい汁あと一歩染みこんでほしい仕上がり。
ウマ味凝縮あと一歩な仕上がり。
少し歯切れ悪い仕上がり。
カタメな食感のもの。
カタメな仕上がりのもの。
つるりとした舌触りのもの。
いつもより柔らかめのもの。
柔らかめな極太麺、液体アブラ纏ってる。
汁絡み、歯切れ楽しい、パッツ麺。
液体アブラ纏ったムッチムチ麺。
ザックザク、味しみ感があるもの。
柔らかい麺。汁染み感もあり。
パツ食感に汁染みたもの。
チョイデロな柔らかめのもの。
パツパツ麺。汁がほど良く絡む。
ザクザクと食える麺。
ウマい。メッチャ柔らかプッルプル。
柔らかめな仕上がり嬉しい味染み麺。
柔らかめで醤油染みててウマい。
コレ好き。味染みまくりィ。
プリとした食感、ズババと啜れる俺好みのもの。
クッニュクニュ。アブラ纏ってウマい。
柔らかくて味染み感バツグン。
ザックザク頬張れて、口溶け感俺好み。
みた麺、喰い出したら夢中。奮え止まらない。
液体アブラ纏った麺、汁染み具合俺好み。
ちょいパツな仕上がりに汁メッチャ染みててウマし。
プルンと踊る食感楽しめるもの。俺好み。
汁メッチャ染みてて、たまらなくウマい。
柔らかくて甘ウマ汁染みててウンメ〜〜ッ。
醤油染みたもの。玉子絡めてウマい。
柔らか嬉しい、喰い出したらとまんないもの！
柔らかくてウッメェェッ！
ホクと柔らか味染みててウンメ〜ッ！
ユッルユルに柔らか激しく俺好みのもの。メッチャウマ！
醤油染みててプルプル食感の太麺、メッチャウンメ〜ッ！
液体アブラ甘んめ〜っ！醤油効いてウンメ〜ッ！
ュ麺ヤバすぎ、ブタプリップリぃ！
ウンメ〜ッ！最ッ高でしょ。
ウマい、ウマ過ぎる。押し寄せる多幸感。夢見心地で貪るぅ！
デロンデロンなデロ麺がメッチャ柔らかくて、たまんない。極めて俺好みのもの。
髑髏汁染みた麺、超堪んない！
コレ好きィ！ツルンッ！モチッ！として汁メッチャ染みたもの。ウンメ〜ッ！
甘ウマ汁染みてて、トロける柔らかさの俺好みな麺。ウンメ〜！
クニュとした食感の麺がアブラ纏ってウンメ〜！
モソとした素朴な食感俺好み。メッチャウンメ〜ッ！
プルプル食感、俺好み。メッチャウンメ〜ッ！
メッチャ味染みた、口の中で、ふあとほどける、ほぼ咀嚼不要なもの。最ッ高に俺好み。
ウッメェェェェェッッ！！クニュとした食感の、味染みた最ッ高にウマい麺ッ！！
このクニュ感、この柔らかさ、至高過ぎィ！
クニュッと柔らか、ふあとほどける口溶け、最ッ高でしょ！
柔らか！味染み！アブラ絡んで、神域ッ！
ムチとした麺、ザクと啜ってウッメェェッ！神域のなか、夢中で掻き込む。
柔らかな仕上がり嬉しい、味メッチャ染みた最ッ高にウマい神麺！！
汁染みた麺ハフハフ啜る。ウマ過ぎィ！俺の理想二郎のひとつ降臨してた。
この麺、至高過ぎぃ！クニュ食感に、汁染みた神域のもの。
神域のデッロデロ。汁染み極まり、奮えて啜る。至高過ぎィ！
この麺、神話級ッ！語り継がれるべき味染み感。神と戯れてたら丼カラになってた。
歯切れ最高のプツパツ麺。メッチャクチャ俺好みィ！神麺ここに降臨。
プルップルに柔らかい、最ッ高な食感の麺。旨味濃厚汁染みて、奮えるしかない神域の麺！
"""

    chain = PrepareChain(text)
    triplet_freqs = chain.make_triplet_freqs()
    chain.save(triplet_freqs, True)