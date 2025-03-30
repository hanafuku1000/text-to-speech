import os
from google.cloud import texttospeech
import io
import streamlit as st
from google.cloud import secretmanager
import tempfile



#=============================================================
# 公開する場合の、api_keyの設定
#=============================================================
def access_secret_version(project_id, secret_id, version_id="latest"):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("utf-8")
    except Exception as e:
        st.error(f"Secret Managerからシークレットの取得に失敗しました: {e}")
        raise RuntimeError("認証情報の取得が失敗しました。")

# プロジェクトIDを指定（Google Cloud プロジェクトID）
project_id = "udemy-text-to-speach-455123"
secret_id = "secret_key20250330"

# シークレットを取得
api_key = access_secret_version(project_id, secret_id)
#print(f"取得したAPIキー: {api_key}")

# Secret Managerから取得した認証情報を一時ファイルに保存
try:
    # 一時ファイルの作成と環境変数の設定
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(api_key.encode("utf-8"))
        temp_file_path = temp_file.name
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

    # 認証後の処理（音声合成など）
    client = texttospeech.TextToSpeechClient()
    # 必要な処理をここで実行...

finally:
    # 一時ファイルの削除
    os.remove(temp_file_path)


#=============================================================
#ローカルで使用する場合は、secret.jsonを読込むだけでイケル
#=============================================================
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"



#=============================================================
# 音声を合成する関数
#=============================================================
def synthesize_speech(text,lang="日本語",gender="default"):
    


    # TextToSpeechClientをインスタンス化＝APIを使用できるようにする
    # Google Cloudの認証情報を同時に以下の1行で確認
    client = texttospeech.TextToSpeechClient()

    # 読み上げテキストの設定
    synthesis_input = texttospeech.SynthesisInput(text=text) #読み上げるテキストを指定

    # Build the voice request, select the language code ("en-US") and the ssml
    # 音声と言語の設定
    voice = texttospeech.VoiceSelectionParams(
        
        #言語と声の性別を設定
        language_code=lang_code[lang], ssml_gender= gender_type[gender] #gender_type辞書型から性別を取得して指定

    )

    # 生成音声の種類（拡張子）
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # APIの呼び出し
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response


#=============================================================
# # 辞書型変数の定義
#=============================================================

#声の性別変数（辞書型）
gender_type = {
    "default": texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED, #デフォルト
    "male": texttospeech.SsmlVoiceGender.MALE, #男性声
    "female": texttospeech.SsmlVoiceGender.FEMALE, #女性声
        
    "neutral": texttospeech.SsmlVoiceGender.NEUTRAL, #ニュートラル（中性
}

#言語の変数
lang_code = {
    "日本語":"ja-JP", #日本語
    "英語":"en-US", #英語
    "中国語":"zh-CN", #中国語

}

#読み上げテキストの指示方法
options_dict = {
    "直接入力": 1,  # 選択肢「直接入力」
    "ファイルを読込む": 2  # 選択肢「ファイルを読込む」
}




#=============================================================
# 画面作成（streamlit）
#=============================================================
st.title("音声出力アプリ") #タイトル

st.write("#### データ準備") #説明文
st.write("音声合成APIを使用して音声を生成します。") #説明文





# ユーザーが選択するリストボックス
selected_option = st.selectbox("入力の種類:", list(options_dict.keys()))

# 選択されたオプションの値を取得
selected_value = options_dict[selected_option]


input_data =None #初期値の設定
lang ="日本語" #言語の初期値
gender = "default" #性別の初期値

# 選択されたオプションごとによる処理の分岐
if selected_value == 1:
    input_data = st.text_area("入力してください:") #直接入力用のテキストボックスが作成される
    

elif selected_value == 2:
    uploaded_file = st.file_uploader("ファイルを選択してください:", type=["txt"])

    if uploaded_file:
        # テキストファイルの内容を読み取り
        input_data = uploaded_file.read().decode("utf-8")  # ファイルの内容を文字列として取得
        


if input_data is not None:
    st.write("入力データ確認：")
    st.write(input_data) #入力データの表示
    # ユーザーが選択するリストボックス
    st.markdown("### パラメータ設定")
    st.subheader("言語と話者の性別選択")
    gender = st.selectbox("読み上げ声の選択", list(gender_type.keys())) #性別の選択肢
    lang = st.selectbox("読み上げ言語の選択", list(lang_code.keys())) #性別の選択肢
    st.markdown("### 音声合成")
    st.write("コチラの文章で音声ファイルの生成をおこないますか？")
    
    if st.button("開始"):
        comment = st.empty()
        comment.write("音声出力を開始します")
        response = synthesize_speech(input_data,lang,gender)  # 音声合成関数を呼び出す

        #音声の再生
        st.audio(response.audio_content) #音声ファイルを再生
        comment.write("完了しました")


