from b2sdk.v1 import InMemoryAccountInfo, B2Api, Bucket
import cloudinary
from os import getenv, path

cloudinary.config( 
  cloud_name = getenv('CLOUD_NAME'), 
  api_key = getenv('CLOUD_API_KEY'), 
  api_secret = getenv('CLOUD_API_SECRET'),
#   secure = True
)

import cloudinary.uploader
import cloudinary.api

# Import the CloudinaryImage and CloudinaryVideo methods for the simplified syntax used in this guide
from cloudinary import CloudinaryImage
import random


def generate_html_css(client_name, logo_url, primary_color, welcome_message, placeholder_text, hide_branding):
    if not welcome_message:
        greetings = 'Hi there 👋 <br>How can I help you today?'
    else:
        greetings = welcome_message
        
    if not placeholder_text:
        placeholder = "Enter a query..."
    else:
        placeholder = placeholder_text
        
    html_content = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <link rel="stylesheet" href="{client_name}_style.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <script src="script.js" defer></script>
    
</head>

<body >
    <button class="chatbot-toggler">
        <span class="material-symbols-outlined">mode_comment</span>
        <span class="material-symbols-outlined">close</span>
    </button>
    <div class="chatbot">
        <header>
            <img src="{logo_url}" alt="">
            <h2>{client_name}</h2>
            <span class="close-btn material-symbols-outlined">close</span>
        </header>
        <ul class="chatbox">
            <li class="chat incoming">
                <span id="robot" class="material-symbols-outlined">smart_toy</span>
                <p>{greetings}</p>
            </li>

        </ul>
        <div class="chat-input">
            <textarea placeholder={placeholder} required>
            </textarea>
            <span id="send-btn" class="material-symbols-outlined">
                send
            </span>
        </div>
        <div class="powered">
            Powered by &nbsp;&nbsp;&nbsp;&nbsp; <a href="https://contexxai.com" target="_blank"><img src="./logo.png" alt=""><b>Contexx AI</b></a>
        </div>
    </div>
    
</body>
</html>
    """

    css_content = f"""
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "Poppins", sans-serif;
    }}
    body {{
    }}

    #chatbot-ui {{

        width: 491px; 
        height: 90vh; 
        position: fixed; 
        right: 0;
        bottom: 0;
        border: none; 
        z-index: 9999;
        border-radius: 10px;
    }}

    .chatbot-toggler {{
        position: fixed;
        right: 10px;
        bottom: 5px;
        height: 50px;
        width: 50px;
        color: #fff;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        outline: none;
        cursor: pointer;
        background: {primary_color};
        border-radius: 50%;
        transition: all 0.2s ease;
    }}
    .show-chatbot .chatbot-toggler {{
        transform: rotate(90deg);
    }}
    .chatbot-toggler span {{
        position: absolute;
    }}
    .show-chatbot .chatbot-toggler span:first-child,
    .chatbot-toggler span:last-child {{
        opacity: 0;
    }}
    .show-chatbot .chatbot-toggler span:last-child {{
        opacity: 1;
    }}
    .chatbot {{
        position: fixed;
        right: 10px;
        bottom: 60px;
        width: 340px;
        transform: scale(0.5);
        opacity: 0;
        pointer-events: none;
        overflow: hidden;
        background: #fff;
        border-radius: 10px;
        transform-origin: bottom right;
        box-shadow: 0 0 128px 0 rgba(0,0,0,0.1),
                    0 32px 64px -48px rgba(0,0,0,0.5);
        transition: all 0.1s ease;
    }}
    .show-chatbot .chatbot {{
        transform: scale(1);
        opacity: 1;
        pointer-events: auto;
    }}
    .chatbot header {{
        background: {primary_color};
        border-top-right-radius: 10px;
        border-top-left-radius: 10px;
        border-bottom: 2px solid {primary_color};
        padding: 5px 0;
        text-align: center;
        position: relative;
        display: flex;
        align-items: center;
        padding-left: 20px;
    }}
    .chatbot header h2 {{
        color: white;
        font-size: 14px;
    }}
    .chatbot header span {{
        position: absolute;
        right: 10px;
        top: 50%;
        color: #fff;
        cursor: pointer;
        display: none;
        transform: translateY(-50%);
    }}
    .chatbot header img {{
    width: 50px;
    border-radius: 50%;
    margin-right: 10px;
    }}
    .powered, .powered a {{
        display: flex;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        color: white;
        background-color: {primary_color};
        font-size: 10px;
        height: 30px;
    }}
    .powered img {{
    width: 30px;
    border-radius: 50%;
    margin-right: 0px;
    }}
    .chatbot .chatbox {{
        height: 75vh;
        overflow-y: auto;
        padding: 15px 10px 80px;
    }}
    .chatbox .chat {{
        display: flex;
    }}
    .chatbox .incoming span {{
        height: 32px;
        width: 32px;
        color: #fff;
        align-self: flex-end;
        background: {primary_color};
        text-align: center;
        line-height: 32px;
        border-radius: 4px;
        margin: 0 10px 7px 0;
    }}
    #robot {{
        height: 32px;
        width: 32px;
        color: #fff;
        align-self: flex-end;
        background: {primary_color};
        text-align: center;
        line-height: 32px;
        border-radius: 4px;
        margin: 0 10px 7px 0;
    }} 
    .chatbox .outgoing {{
        margin: 20px 0;
        justify-content: flex-end;
    }}
    .chatbox .chat p {{
        color: #fff;
        max-width: 75%;
        white-space: pre-wrap;
        font-size: 0.95rem;
        padding: 12px 16px;
        border-radius: 10px 10px 0 10px;
        background: {primary_color};
    }}

    .chatbox .chat p.error {{
        color: #721c24;
        background: #f8d7da;
    }}

    .chatbox .incoming p {{
        color: #1F2937;
        background: #f2f2f2;
        border-radius: 10px 10px 10px 0;
    }}

    .chatbot .chat-input {{
        position: absolute;
        bottom: 6%;
        width: 100%;
        display: flex;
        gap: 5px;
        background: #fff;
        padding: 5px 20px;
        border-top: 1px solid #ccc;
    }}
    .chat-input textarea {{
        height: 55px;
        width: 100%;
        border: none;
        outline: none;
        max-height: 180px;
        font-size: 0.95rem;
        resize: none;
        padding: 16px 15px 16px 0;
    }}
    .chat-input span{{
        align-self: flex-end;
        height: 55px;
        line-height: 55px;
        color: #1F2937;
        font-size: 1.35rem;
        cursor: pointer;
        visibility: hidden;
    }}

    .chat-input textarea:valid ~ span {{
        visibility: visible;
    }}

    @media(max-width: 490px) {{
        #chatbot-ui {{
            width: 100%; 
            height: 100%; 
            position: fixed; 
            right: 0;
            bottom: 0;
            border-radius: 0;
        }}
        .chatbot {{
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            border-radius: 0;
        }}
        .chatbot header {{
            border-radius: 0;
        }}
        .chatbot .chatbox {{
            height: 90%;
        }}
        .chatbot header span {{
            display: block;
        }}
    }}
    """
    files = {}
    files['html_content']=html_content
    files['css_content']=css_content   
    return files

def save_files(html_content, css_content, client_name, user_external_d):
    
    html_file_path = f'{client_name + '_' + str(user_external_d)}_chatbot.html'
    css_file_path = f'{client_name + ' '+ str(user_external_d)}_style.css'

    with open(html_file_path, 'w', encoding='utf-8') as html_file:   
        html_file.write(html_content)

    with open(css_file_path, 'w', encoding='utf-8') as css_file:
        css_file.write(css_content)
    file_path = {}
    file_path['html_file_path']=html_file_path
    file_path['css_file_path']=css_file_path
    file_path['client_name']=client_name 
    
    return file_path




def upload_to_backblaze(html_file_path, css_file_path, bucket_name, application_key_id, application_key):
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)

    # Authenticate with your Backblaze B2 credentials
    b2_api.authorize_account("production", application_key_id, application_key)

    # Get the bucket you want to upload the files to
    bucket = b2_api.get_bucket_by_name(bucket_name)
    
    # Upload the HTML file
    with open(html_file_path, 'rb') as html_file:
        print(html_file)
        bucket.upload_bytes(html_file.read(), html_file_path)

    # Upload the CSS file
    with open(css_file_path, 'rb') as css_file:
        print(css_file)
        bucket.upload_bytes(css_file.read(), css_file_path)

    print(f'Files {html_file_path} and {css_file_path} uploaded successfully.')
    print(html_file_path)
    print(css_file_path)
    
    return {html_file_path, css_file_path}
    
    
def upload_logo(image_path):
  try:
        # Upload the image to Cloudinary
      
        response = cloudinary.uploader.upload(image_path)
        
        # The response contains the URL of the uploaded image
        print(response)
        print("Image uploaded successfully.")
        print("URL: ", response['secure_url'])
        
        return response
  except Exception as e:
        print("Error uploading image: ", str(e))
        return None


