import streamlit as st
from PIL import Image
import base64

import time

# with st.empty():
#     for seconds in range(6):
#         st.write(f"⏳ {seconds} seconds have passed")
#         time.sleep(1)
#     st.write("✔️ 1 minute over!")

placeholder = st.empty()

# Replace the placeholder with some text:
placeholder.text("Hello")

# Replace the text with a chart:
placeholder.line_chart({"data": [1, 5, 2, 6]})

# Replace the chart with several elements:
with placeholder.container():
    st.write("This is one element")
    st.write("This is another")

# Clear all those elements:
placeholder.empty()


# st.secrets["public_gsheets_url"]
#
# st.json({'foo':'bar','fu':'ba'})
# st.write(['st', 'is <', 3]) # see *
#
# file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
# if file is not None:
#     st.image(file)
#     st.write(file)
#     img = Image.open(file)
#     st.write(img)
#     img_bytes = file.read()
#     encoded_img = base64.b64encode(img_bytes).decode('utf-8')
#     st.write(encoded_img)
#
# def load_image(image_file):
#     img = Image.open(image_file)
#     return img





