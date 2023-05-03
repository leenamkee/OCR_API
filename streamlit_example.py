import streamlit as st
from PIL import Image
import base64

st.json({'foo':'bar','fu':'ba'})
st.write(['st', 'is <', 3]) # see *

file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if file is not None:
    st.image(file)
    st.write(file)
    img = Image.open(file)
    st.write(img)
    img_bytes = file.read()
    encoded_img = base64.b64encode(img_bytes).decode('utf-8')
    st.write(encoded_img)

def load_image(image_file):
    img = Image.open(image_file)
    return img





