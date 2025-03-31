import os
import tempfile
import logging
from google.cloud import texttospeech
from google.cloud import secretmanager
import streamlit as st
import io

def check_credentials():
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not os.path.exists(credentials_path):
        raise FileNotFoundError(f"認証ファイルが見つかりません: {credentials_path}")
    


# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def access_secret_version(project_id: str, secret_id: str, version_id="latest") -> str:
    """
    Secret Managerからシークレットを取得する関数
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        logging.info(f"Secret Managerからシークレットを正常に取得しました: {secret_id}")
        return response.payload.data.decode("utf-8")
    except Exception as e:
        logging.error(f"Secret Managerからシークレットの取得に失敗しました: {e}")
        raise RuntimeError(f"Secret Managerからのシークレット取得に失敗しました: {e}")

def set_google_credentials(is_local: bool):
    """
    Google Cloud認証情報を設定する関数（ローカルと公開環境に対応）
    """
    if is_local:
        # ローカル環境: secret.jsonを使用
        credentials_path = "secret.json"
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"認証ファイルが見つかりません: {credentials_path}")
        return credentials_path
    else:
        # 公開環境: Secret Managerから認証情報を取得
        project_id = "udemy-text-to-speach-455123"
        secret_id = "secret_key20250330"
        api_key = access_secret_version(project_id, secret_id)
        with tempfile.NamedTemporaryFile(delete=True, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(api_key)
            temp_file_path = temp_file.name
            os.chmod(temp_file_path, 0o400)  # アクセス権を制限
        return temp_file_path

def configure_environment():
    """
    環境設定を行う関数
    """
    check_credentials()
    environment = os.environ.get("ENVIRONMENT", "local").lower()
    if environment not in ["local", "production"]:
        raise ValueError(f"無効な環境設定: {environment}")
    is_local = environment == "local"
    credentials_path = set_google_credentials(is_local)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    logging.info(f"認証情報を設定しました (Path: {credentials_path})")

# メイン処理
try:
    # 環境設定
    configure_environment()

    # Text-to-Speechクライアントの初期化
    client = texttospeech.TextToSpeechClient()
    logging.info("Google Text-to-Speech Clientが正常に初期化されました")
except Exception as e:
    logging.error(f"処理中にエラーが発生しました: {e}")


#=============================================================
# 音声を合成する関数
#=============================================================
def synthesize_speech(text, lang="日本語", gender="default"):
    try:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code[lang],
            ssml_gender=gender_type[gender]
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response
    
    except Exception as e:
        logging.error(f"音声合成中にエラーが発生しました: {e}")
        raise RuntimeError("音声合成に失敗しました。")



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
        try:
            comment = st.empty()
            comment.write("音声出力を開始します")
            response = synthesize_speech(input_data, lang, gender)
            st.audio(response.audio_content)
            comment.write("完了しました")
        except Exception as e:
            st.error(f"音声合成に失敗しました: {e}")


import subprocess

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    subprocess.run(["streamlit", "run", "app.py", "--server.port", str(port), "--server.address", "0.0.0.0"])