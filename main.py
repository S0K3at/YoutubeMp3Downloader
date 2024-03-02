from flask import Flask, request, Response
from pytube import YouTube
import os
import time
from urllib.parse import quote

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def safe_remove(file_path):
    """파일을 안전하게 삭제하는 함수."""
    try:
        os.remove(file_path)
        print(f"File successfully removed: {file_path}")
    except PermissionError as e:
        print(f"PermissionError: {e}, file may be in use.")

def generate_file_stream(file_path):
    """파일 스트림 생성기."""
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            yield chunk

@app.route('/download_audio/<youtube_id>', methods=['GET'])
def download_audio(youtube_id):
    video_url = f"https://www.youtube.com/watch?v={youtube_id}"
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    default_filename = audio_stream.default_filename
    filename_without_extension = os.path.splitext(default_filename)[0]
    download_path = os.path.join(DOWNLOAD_FOLDER, filename_without_extension + '.mp3')

    if not os.path.exists(download_path):
        audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=filename_without_extension + '.mp4')
        os.rename(os.path.join(DOWNLOAD_FOLDER, filename_without_extension + '.mp4'), download_path)

    encoded_filename = quote(filename_without_extension + '.mp3')
    response = Response(generate_file_stream(download_path), content_type='audio/mpeg')
    response.headers['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'

    @response.call_on_close
    def on_close():
        safe_remove(download_path)

    return response

if __name__ == '__main__':
    app.run(debug=True)
