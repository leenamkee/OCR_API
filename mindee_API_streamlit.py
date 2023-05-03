import streamlit as st
from mindee import Client, documents
import pandas as pd
from PIL import Image
import base64

# Init a new client
mindee_client = Client(api_key="3cdc41fac36e7f877c7ca11b23e97708")

st.set_page_config(layout="wide")
st.title("Invoice Data Extraction App")

fileurl = st.text_input('Input URL of invoice image: ')
# st.write('sample: https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png')
st.text('sample: https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png')
st.write('Or')
file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

try:

    if file is not None:
        st.image(file)
        img_bytes = file.read()
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        input_doc = mindee_client.doc_from_file(file)
        api_response = input_doc.parse(documents.TypeInvoiceV4)
    else:
        # Load a file from disk or using URL
        fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdyPlb5%2FbtscPcNUgnr%2FCkjWKD53kndLyUXeolKYq0%2Fimg.png"
        st.image(fileurl)
        input_doc = mindee_client.doc_from_url(fileurl)

        # Parse the document by passing the appropriate type
        api_response = input_doc.parse(documents.TypeInvoiceV4)

    # invoice header data
    predictions_header = api_response.__dict__['http_response']['document']['inference']['prediction']
    # features_header = api_response.__dict__['http_response']['document']['inference']['product']['features'][:-2]
    features_header = list(predictions_header.keys())
    features_header.remove('line_items')
    df_header = pd.DataFrame()

    for i in range(len(features_header)):
        predictions_header_dict = {}
        if isinstance(predictions_header[features_header[i]], list) and len(
                predictions_header[features_header[i]]) == 1:
            predictions_header_dict = predictions_header[features_header[i]][0]
            last_value = list(predictions_header_dict.keys())[-1]
            # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
            df_header[features_header[i]] = [predictions_header_dict[last_value]]
        elif isinstance(predictions_header[features_header[i]], list) and len(
                predictions_header[features_header[i]]) == 0:
            # st.write(f'{features_header[i]}: N/A')
            df_header[features_header[i]] = [None]
        elif isinstance(predictions_header[features_header[i]], dict):
            predictions_header_dict = predictions_header[features_header[i]]
            last_value = list(predictions_header_dict.keys())[-1]
            # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
            df_header[features_header[i]] = [predictions_header_dict[last_value]]
    df_header.dropna(inplace=True, axis=1)
    df_header = df_header.transpose()
    df_header.rename(columns={0: 'value'}, inplace=True)
    st.subheader('Invoice Header')
    st.write(df_header)

    # invoice item data
    predictions_line_items = api_response.__dict__['http_response']['document']['inference']['prediction']['line_items']
    # line item data frame
    df = pd.DataFrame(predictions_line_items)
    df = df.loc[:, ['confidence', 'description', 'quantity', 'unit_price', 'total_amount']]
    # Display the DataFrame
    st.subheader('Invoice Items')
    st.write(df)


    show_json = False  # boolean variable to track whether to show the JSON or not

    if st.button("Show/Hide JSON"):
        show_json = not show_json  # invert the boolean value

    if show_json:
        # code to display the JSON
        st.json(predictions_header)
    else:
        st.write(':)')



    # Create a button to show/hide the JSON file
    # if st.button("Show/Hide JSON"):
    #
    #     # Show the JSON file
    #     st.json(predictions_header)
    #
    #     # Set a flag to indicate that the button has been clicked
    #     button_clicked = True
    # else:
    #     # If the button has not been clicked, set the flag to False
    #     button_clicked = False
    #
    # # If the button has been clicked, show a message indicating that the JSON file is hidden
    # if button_clicked:
    #     st.write("Click the button again to hide the JSON file.")

except:
    st.write("Error: Could not extract data from the provided URL or file. Please check and try again.")

# Add an input box for the user to enter a URL

#
# url = ''
# url = st.text_input("Enter image URL:")
#
# if not url:
#     url = 'https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png'
#
# if url:
#     try:
#         # Load the image from the URL
#         input_doc = mindee_client.doc_from_url(url)
#
#         # Parse the document by passing the appropriate type
#         api_response = input_doc.parse(documents.TypeInvoiceV4)
#
#         # invoice header data
#         predictions_header = api_response.__dict__['http_response']['document']['inference']['prediction']
#         features_header = api_response.__dict__['http_response']['document']['inference']['product']['features'][:-2]
#
#         # invoice item data
#         predictions_line_items = api_response.__dict__['http_response']['document']['inference']['prediction']['line_items']
#
#         # data frame
#         df = pd.DataFrame(predictions_line_items)
#
#         for i in range(len(features_header)):
#             predictions_header_dict = {}
#             if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
#                 predictions_header_dict = predictions_header[features_header[i]][0]
#                 last_value = list(predictions_header_dict.keys())[-1]
#                 df[features_header[i]] = predictions_header_dict[last_value]
#             elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
#                 df[features_header[i]] = "N/A"
#             elif isinstance(predictions_header[features_header[i]], dict):
#                 predictions_header_dict = predictions_header[features_header[i]]
#                 last_value = list(predictions_header_dict.keys())[-1]
#                 df[features_header[i]] = predictions_header_dict[last_value]
#
#         # Display the DataFrame
#         st.write(df)
#         st.image(url)
#     except:
#         st.write("Error: Could not extract data from the provided URL. Please check the URL and try again.")





