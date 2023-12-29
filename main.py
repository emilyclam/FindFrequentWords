import moviepy.editor as mp
import speech_recognition as sr
import nltk
from nltk.corpus import stopwords
from janome.tokenizer import Tokenizer
import re
nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


def vid_to_text(video_path):
    clip = mp.VideoFileClip(video_path)
    audio = clip.audio
    recognizer = sr.Recognizer()
    temp_audio_path = "temp_audio.wav"
    audio.write_audiofile(temp_audio_path)

    # Use the temporary audio file for recognition
    with sr.AudioFile(temp_audio_path) as source:
        audio_data = recognizer.record(source)

    return recognizer.recognize_google(audio_data)


def get_top_words_sents(text, num, language="english"):
    words = nltk.word_tokenize(text)
    # only include alphabetical words (eg NOT 's)
    words = [word.casefold() for word in words if word.isalpha()]

    # remove stop words
    stop_words = set(stopwords.words(language))
    words = [
        word for word in words if word not in stop_words
    ]

    # tag parts of speech
    #words_pos = nltk.pos_tag(words)
    #print(words_pos)

    # lemmatizing the words (running -> run)
    lemmatizer = nltk.WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # get [num] most common words
    freq = nltk.FreqDist(words)
    common_words = freq.most_common(num)
    top_words = [word for word, freq in common_words]

    # get sentences with top words
    sents = {
        word: [] for word in top_words
    }

    for sent in nltk.sent_tokenize(text):
        for word in top_words:
            if word in sent.lower():
                sents[word].append(sent)

    return sents


def jpn_split_sents(text):
    sentences = re.split(r"[。！？]", text)
    return sentences


def jpn_process(text, num):
    tokenizer = Tokenizer()
    words = tokenizer.tokenize(text)

    # Extract lemmatized forms (base forms) of tokens and also removes particles, etc
    stop_words = ['する', 'なる', 'ない', 'これ', 'それ', 'id', 'ja', 'いう', 'ある',
                 'あれ', 'それら', 'これら', 'それそれ', 'それぞれ',
                 'その後', '一部', '前', 'よる', '一つ', 'ひとつ', '他',
                 'その他', 'ほか', 'そのほか', 'いる']
    og_words = []
    lemma_words = []
    for word in words:
        if word.part_of_speech.split(',')[0] not in ['助詞', '助動詞', '記号'] and word.base_form not in stop_words:

            og_words.append(word.surface)
            lemma_words.append(word.base_form)

    # remove punctuation (。, 、, ！) etc
    punctuation = ["。", "、", "！", "「", "」", "～", "・", "？"]
    #words = [word for word in words if word not in punctuation]

    # top words
    freq = nltk.FreqDist(lemma_words)
    common_words = freq.most_common(num)
    top_words = [word for word, freq in common_words]

    # get sentences with top words
    sents = {
        word: [] for word in top_words
    }

    for sent in jpn_split_sents(text):
        for top_word in top_words:
            # find all the words that got turned into that lemma
            all_vers = [top_word]
            for i, word in enumerate(lemma_words):
                if word == top_word:
                    all_vers.append(og_words[i])
            # if any version of the top_word is in the sentence, add it
            if any(all_ver in sent.lower() for all_ver in all_vers):
                sents[top_word].append(sent)

    return sents


transcription = vid_to_text("media/short_vid.mp4")
#common_words = get_top_words_sents(transcription, 1)

text = "So he took his axe to the forest, and selected some stout, straight saplings, which he cut down and trimmed of all their twigs and leaves. From these he would make the arms, and legs, and feet of his man. For the body he stripped a sheet of thick bark from around a big tree, and with much labor fashioned it into a cylinder of about the right size, pinning the edges together with wooden pegs. Then, whistling happily as he worked, he carefully jointed the limbs and fastened them to the body with pegs whittled into shape with his knife. By the time this feat had been accomplished it began to grow dark, and Tip remembered he must milk the cow and feed the pigs. So he picked up his wooden man and carried it back to the house with him. During the evening, by the light of the fire in the kitchen, Tip carefully rounded all the edges of the joints and smoothed the rough places in a neat and workmanlike manner. Then he stood the figure up against the wall and admired it. It seemed remarkably tall, even for a full-grown man; but that was a good point in a small boy’s eyes, and Tip did not object at all to the size of his creation.Next morning, when he looked at his work again, Tip saw he had forgotten to give the dummy a neck, by means of which he might fasten the pumpkinhead to the body. So he went again to the forest, which was not far away, and chopped from a tree several pieces of wood with which to complete his work. When he returned he fastened a cross-piece to the upper end of the body, making a hole through the center to hold upright the neck. The bit of wood which formed this neck was also sharpened at the upper end, and when all was ready Tip put on the pumpkin head, pressing it well down onto the neck, and found that it fitted very well. The head could be turned to one side or the other, as he pleased, and the hinges of the arms and legs allowed him to place the dummy in any position he desired."
common_words = get_top_words_sents(text, 5)
#print(common_words)

text = "この国は最高の国です。走る走った走りました走りたい。楽しかったから、また会いましょうね！「じゃな」と言ってた。また走りましょう！それは一つ。一人。猫がいる。"
#text = "走るする なる ない これ それ いう ある あれ それら これら それそれ それぞれ その後 一部 前 よる 一つ ひとつ 他 その他 ほか そのほか いる"
text = "高知県南国市の人たちは毎年、「ごめんなさい」と謝る気持ちを書いたはがきのコンクールを開いています。南国市には「後免（ごめん）」という名前の所があるからです。\
今年も日本のいろいろな所からはがきが届きました。集まった1688枚の中から、賞を決めました。1番の賞になったはがきには、亡くなったおばあさんに51年前のことを謝る\
気持ちが書いてあります。はがきを書いた男性が中学生のとき、学校の運動会でおばあさんが弁当を届けてくれました。しかし、恥ずかしい気持ちがあっておばあさんを家に帰らせてしまいました。\
男性は「ばあちゃん、本当にごめんなさい」とはがきに書きました。コンクールを開いた人は「言うことができなかった『ごめんなさい』をはがきに書いたら、気持ちが楽になると思います」と話しました。"

text_file = open("media/text.txt", "r", encoding='utf8')
text = text_file.read()
text_file.close()
#print(text)
test = jpn_process(text, 3)
print(test)

for word in test.keys():
    print(word + " --")
    for sent in test[word]:
        print("*", sent)
