import streamlink
import subprocess
import os
from google import genai
from google.genai import types
import time
import shutil
from moviepy import VideoFileClip

# --------------------------------------------------------------------------
# --- 설정 (Setup) ---
# --------------------------------------------------------------------------
# 참고: 보안을 위해 API 키를 코드에 직접 하드코딩하는 것보다
# 환경 변수로 관리하는 것이 더 안전합니다.
# 예: API_KEY = os.getenv("GEMINI_API_KEY")
# TODO: Enter your Gemini API Key here
API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=API_KEY)

# --------------------------------------------------------------------------
# --- 함수 정의 (Function Definitions) ---
# --------------------------------------------------------------------------

def create_directories():
    """결과물을 저장할 디렉터리가 없으면 생성합니다."""
    for path in ["./video", "./audio", "./text", "./completed-video"]:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"'{path}' 디렉터리를 생성했습니다.")


def download_hls_video(url, output_filename):
    """
    HLS 동영상을 다운로드하는 함수
    Args:
        url (str): M3U8 URL
        output_filename (str): 저장할 파일 이름
    """
    print(f"'{output_filename}' 다운로드를 시작합니다...")
    try:
        streams = streamlink.streams(url)
        if not streams:
            print("❌ 스트림을 찾을 수 없습니다.")
            return False

        best_stream = streams["best"]
        print(f"최상 화질 스트림 URL을 찾았습니다. ffmpeg로 다운로드합니다.")

        # ffmpeg를 사용하여 다운로드
        cmd = [
            'ffmpeg',
            '-y',  # 덮어쓰기 허용
            '-i', best_stream.url,
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            output_filename
        ]

        # -loglevel quiet 옵션으로 ffmpeg의 상세 로그를 숨깁니다.
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ 다운로드 완료: {output_filename}")
        return True

    except Exception as e:
        print(f"❌ 다운로드 중 오류 발생: {e}")
        return False


def convert_mp4_to_mp3(mp4_file_path, mp3_file_path):
    """
    MP4 영상 파일을 MP3 오디오 파일로 변환하는 함수
    Args:
        mp4_file_path (str): 변환할 MP4 파일의 경로
        mp3_file_path (str): 저장할 MP3 파일의 경로
    """
    print(f"'{mp4_file_path}'를 MP3로 변환합니다...")
    try:
        # moviepy.editor를 직접 사용하여 호출
        # Note: In recent moviepy versions, VideoFileClip is in moviepy.editor or mostly moviepy
        # If the user has an issue with imports, we stick to what worked or the standard
        video_clip = VideoFileClip(mp4_file_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(mp3_file_path, logger=None)
        audio_clip.close()
        video_clip.close()
        print(f"✅ 변환 완료: {mp3_file_path}")
        return True
    except Exception as e:
        print(f"❌ MP3 변환 중 오류 발생: {e}")
        return False


def transcribe_large_audio(audio_file_path):
    """
    Gemini를 사용하여 오디오 파일을 텍스트로 변환하는 함수
    gemini-3-pro-preview 모델 사용
    """
    try:
        print(f"🎧 '{audio_file_path}' 파일을 Gemini에 업로드하여 텍스트 변환을 시작합니다.")

        # Gemini File API를 사용하여 파일 업로드 (Retry Logic)
        audio_file_local = None
        upload_retries = 3
        for attempt in range(upload_retries):
            try:
                # 'path/to/sample.mp3'
                with open(audio_file_path, 'rb') as f:
                    # upload method expects 'file' argument which can be a path or file-like object
                    # usage from prompt: client.files.upload(file="path/to/sample.mp3")
                    audio_file_local = client.files.upload(file=audio_file_path)
                break
            except Exception as e:
                print(f"⚠️ 파일 업로드 시도 {attempt + 1} 실패: {e}")
                if attempt < upload_retries - 1:
                    time.sleep(5)
                else:
                    return f"❌ 파일 업로드 실패: {e}"

        print(f"📡 파일 업로드 완료. 처리 대기 중... (File Name: {audio_file_local.name})")
        
        # 파일 처리가 완료될 때까지 대기
        # The new SDK might handle this differently, but we assume similar state checks apply 
        # based on previous experience or we use a loop.
        # The prompt examples didn't explicitly show waiting logic for 'upload', 
        # but usually heavy files need processing.
        # Since the example code didn't wait loop for processing in the prompt (it just did generate_content immediately),
        # I will assume generate_content might handle it or it's fast enough.
        # HOWEVER, for safety, I will keep the check if the property is available.
        # If 'state' is not available on the returned object easily, we might skip.
        # Let's check state if valid.
        
        while audio_file_local.state.name == "PROCESSING":
             print("... 처리 중 ...")
             time.sleep(2)
             try:
                 audio_file_local = client.files.get(name=audio_file_local.name)
             except Exception as e:
                 pass

        if audio_file_local.state.name != "ACTIVE":
             raise ValueError(f"File processing failed. State: {audio_file_local.state.name}")
        
        print("✅ 파일 처리 완료 (ACTIVE).")
        print("🤖 Gemini 모델에 텍스트 변환 요청 중...")
        
        # Using gemini-3-pro-preview as requested
        model_name = "gemini-3-pro-preview"
        
        prompt = """
        Process the audio file and generate a detailed verbatim transcription.
        
        Requirements:
        1. Transcript ENTIRETY of the audio verbatim. Do NOT summarize or omit any details.
        2. Do NOT identify or label distinct speakers. Treat it as a continuous stream of text.
        3. Do NOT include timestamps at all.
        """

        max_retries = 5
        for attempt in range(max_retries):
            try:
                print(f"🔄 텍스트 변환 시도 {attempt + 1}/{max_retries}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, audio_file_local],
                    config=types.GenerateContentConfig(
                        temperature=0.0
                    )
                )

                print("✅ 텍스트 변환이 완료되었습니다.")
                return response.text
            except Exception as e:
                print(f"⚠️ 텍스트 변환 시도 {attempt + 1} 실패: {e}")
                if "429" in str(e) or "Resource has been exhausted" in str(e):
                     print("⏳ Quota exceeded. Waiting longer...")
                     time.sleep(30 + (2 ** attempt)) 
                elif attempt < max_retries - 1:
                    time.sleep(5 * (2 ** attempt)) 
                else:
                    raise e

    except Exception as e:
        return f"❌ 오디오 변환 중 오류가 발생했습니다: {e}"


def translate_text_to_korean(text):
    """Gemini 모델을 사용하여 텍스트를 한국어로 번역하는 함수"""
    if not text or text.strip() == "":
        return "번역할 텍스트가 없습니다."

    print("🤖 Gemini 모델을 통해 한국어로 번역 중입니다...")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:            
            prompt_text = f"""
            You are a professional translator. Translate the following text into natural-sounding Korean.
            If the text is too long, translate it faithfully without summarizing.
            
            Text:
            {text}
            """

            print(f"🔄 번역 시도 {attempt + 1}/{max_retries}...")
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=prompt_text
            )
            
            if response.text:
                return response.text
            else:
                return "❌ 번역 결과가 비어있거나 유효하지 않습니다."
        
        except Exception as e:
            print(f"⚠️ 번역 시도 {attempt + 1} 실패: {e}")
            if "429" in str(e) or "Resource has been exhausted" in str(e):
                    print("⏳ Quota exceeded. Waiting longer...")
                    time.sleep(30 + (2 ** attempt)) 
            elif attempt < max_retries - 1:
                time.sleep(5 * (2 ** attempt)) 
            else:
                return f"❌ 번역 중 오류 발생(최대 재시도 초과): {e}"

    return "❌ 번역 실패: 알 수 없는 오류"


def save_text_to_file(text, file_path):
    """텍스트를 파일에 저장하는 함수"""
    print(f"결과를 '{file_path}' 파일에 저장합니다...")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ 파일 저장 완료: {file_path}")
    except Exception as e:
        print(f"❌ 파일 저장 중 오류 발생: {e}")


def process_video_workflow(filename_base):
    """
    비디오 파일을 처리하여 오디오 추출, 텍스트 변환, 번역을 수행하는 워크플로우
    """
    video_file = f"./video/{filename_base}.mp4"
    audio_file = f"./audio/{filename_base}.mp3"
    text_file = f"./text/{filename_base}_original.txt"
    translated_file = f"./text/{filename_base}_translated.txt"

    print(f"\n🎬 Processing: {filename_base}")

    if not os.path.exists(video_file):
        print(f"❌ 비디오 파일을 찾을 수 없습니다: {video_file}")
        return

    # 2. MP3로 변환
    if convert_mp4_to_mp3(video_file, audio_file):
        # 3. 오디오를 텍스트로 변환
        original_text = transcribe_large_audio(audio_file)
        if original_text and not original_text.startswith("❌"):
            # 4. 원본 텍스트 저장
            save_text_to_file(original_text, text_file)

            # 5. 한국어로 번역
            translated_text = translate_text_to_korean(original_text)
            if translated_text and not translated_text.startswith("❌"):
                # 6. 번역된 텍스트 저장
                save_text_to_file(translated_text, translated_file)
                print(f"🎉 '{filename_base}' 작업 완료!")

                # 7. 완료된 영상 이동
                completed_dir = "./completed-video"
                target_path = os.path.join(completed_dir, os.path.basename(video_file))
                print(f"📦 영상을 '{completed_dir}'로 이동합니다...")
                try:
                    shutil.move(video_file, target_path)
                    print(f"✅ 영상 이동 완료: {target_path}")
                except Exception as e:
                    print(f"❌ 영상 이동 중 오류 발생: {e}")
            else:
                print(f"⚠️ 번역 실패: {translated_text}")
        else:
            print(f"⚠️ 텍스트 변환 실패: {original_text}")

# --------------------------------------------------------------------------
# --- 메인 실행 로직 (Main Execution Logic) ---
# --------------------------------------------------------------------------

if __name__ == "__main__":
    create_directories()

    print("--- Video to Text to Korean (gemini-3-pro-preview) ---")
    print("1. 새로운 비디오 다운로드 및 처리")
    print("2. 이미 다운로드된 모든 비디오 처리 (Batch Processing)")
    
    choice = input("선택하세요 (1 또는 2): ").strip()

    if choice == "1":
        video_url = input("HLS 비디오 URL을 입력하세요 (m3u8): ")
        filename_base = input("저장할 파일 이름을 입력하세요 (확장자 제외): ")

        if not video_url or not filename_base:
            print("URL과 파일 이름은 비워둘 수 없습니다.")
        else:
            video_file = f"./video/{filename_base}.mp4"
            # 1. 비디오 다운로드
            if download_hls_video(video_url, video_file):
                process_video_workflow(filename_base)
            else:
                print("❌ 비디오 다운로드 실패로 작업을 중단합니다.")

    elif choice == "2":
        video_dir = "./video"
        if os.path.exists(video_dir):
            files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
        else:
            files = []
        
        if not files:
            print("⚠️ 처리할 비디오 파일이 없습니다.")
        else:
            print(f"📂 총 {len(files)}개의 비디오 파일을 발견했습니다. 순차 처리를 시작합니다.")
            
            sorted_files = sorted(files)
            video_bases = [os.path.splitext(f)[0] for f in sorted_files]
            
            # --- 순차 처리 (Sequential Processing) ---
            for i, base in enumerate(video_bases):
                print(f"\n[{i+1}/{len(video_bases)}] 처리 중: {base}")
                process_video_workflow(base)
                # Rate Limiting을 위해 파일 간 약간의 대기 시간을 둘 수 있음
                if i < len(video_bases) - 1:
                    print("⏳ 다음 파일 처리 전 잠시 대기합니다 (3초)...")
                    time.sleep(3)
            
            print("\n🎉 모든 일괄 처리가 완료되었습니다!")

    else:
        print("❌ 잘못된 선택입니다. 프로그램을 종료합니다.")
