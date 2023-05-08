import streamlit as st
import pdf2image
import zipfile
import io

pop_path = '/poppler/Library/bin'


st.set_page_config(
    page_title="PDF to PNG",
    layout="wide"
)
st.markdown("# :spiral_note_pad: Tom's :blue[PDF] to :red[PNG] Converter :frame_with_picture:")
st.markdown("---")

pdf_uploaded = st.file_uploader("Select a file", type="pdf")
top_container = st.empty()

col1, col2, col3 = st.columns([1, 1, 4])
with top_container, col1:
    button = st.button("Confirm", type='primary')

st.markdown("---")
if button and pdf_uploaded is not None:
    if pdf_uploaded.type == "application/pdf":
        images = pdf2image.convert_from_bytes(pdf_uploaded.read(), poppler_path=pop_path)
        file = io.BytesIO()
        with zipfile.ZipFile(file, 'w') as z:
            for i, page in enumerate(images):
                st.image(page, use_column_width=True)
                img = page
                buf = io.BytesIO()
                img.save(buf, format="png")
                byte_im = buf.getvalue()
                z.writestr(f'image_{i}.png', byte_im)
        z.close()
        file.seek(0)
        zip_contents = file.getvalue()

        with top_container, col2:
            download = st.download_button("Download", data=zip_contents, file_name=f"Images.zip")