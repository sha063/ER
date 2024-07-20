def convert_srt_to_vtt(srt_path, vtt_path):
    with open(srt_path, 'r') as srt_file:
        srt_content = srt_file.read()

    vtt_content = "WEBVTT\n\n" + srt_content.replace(",", ".")

    with open(vtt_path, 'w') as vtt_file:
        vtt_file.write(vtt_content)

convert_srt_to_vtt('a.srt', 'a.vtt')
