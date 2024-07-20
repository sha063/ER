import requests

url = "https://colorize-photo1.p.rapidapi.com/generate_image_prompt"

payload = '-----011000010111000001101001\r\nContent-Disposition: form-data; name="all_standard_filters"\r\n\r\nfalse\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="artistic_filter_id"\r\n\r\n0\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="standard_filter_id"\r\n\r\n1\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="all_artistic_filters"\r\n\r\nfalse\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name="raw_captions"\r\n\r\nfalse\r\n-----011000010111000001101001--\r\n\r\n'
headers = {
    "x-rapidapi-key": "0e9085ba58msh2d6276221a7dfccp123ca5jsnd7f4cc67076a",
    "x-rapidapi-host": "colorize-photo1.p.rapidapi.com",
    "Content-Type": "multipart/form-data; boundary=---011000010111000001101001",
}

response = requests.post(url, data=payload, headers=headers)

print(response.json())
