from optparse import Option
import easyocr as ocr 
import streamlit as st
from PIL import Image
import numpy as np
import re   
import pyrebase


st.sidebar.title("Navigation")
options=st.sidebar.radio('Pages', options=['Main','History'])

firebaseConfig = {
  'apiKey': "AIzaSyCZlxwhnALu8BbUJLxokNtIciQ2jraht0o",
  'authDomain': "firestore-streamlit-bac25.firebaseapp.com",
  'projectId': "firestore-streamlit-bac25",
  'databaseURL':"https://firestore-streamlit-bac25-default-rtdb.europe-west1.firebasedatabase.app/",
  'storageBucket': "firestore-streamlit-bac25.appspot.com",
  'messagingSenderId': "852742296964",
  'appId': "1:852742296964:web:eff8655cb2c8388234f9d1",
  'measurementId': "G-RB84W82VHT"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

db = firebase.database()
storage = firebase.storage()

@st.cache
def load_model():
    reader=ocr.Reader(['en'],model_storage_directory='.')
    return reader

def main_function():
    reader=load_model()  

    st.title("Image Scanner")

    image =st.file_uploader(label="Upload image", type=['png','jpg','jpeg','jfif'])
    result_text=[]
    if image is not None:
        input_image=Image.open(image)
        st.image(input_image)
        
        with st.spinner("Loading"):
            result=reader.readtext(np.array(input_image))
            for text in result:
                result_text.append(text[1])
            # st.write(result_text)

        st.success("here you go!")
    else:
        st.write("Upload an image")
    
    

    col1, col2, col3 = st.columns((1,1,1))

    with col1:
        st.markdown('Email')
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  

        def check_mail(email):   
            with st.spinner("Loading"):
                if(re.search(regex,email)):   
                    st.write(email)  
                    db.child("Email").push(email)


        for i in range(len(result_text)):
            check_mail(result_text[i])


    with col2:
        st.markdown('Mobile')
        regex='^(\\+\\d{1,3}( )?)?((\\(\\d{1,3}\\))|\\d{1,3})[- .]?\\d{3,4}[- .]?\\d{4}$'
        def check_num(num):   
            with st.spinner("Loading"):
                if(re.search(regex,num)):   
                    st.write(num)
                    db.child("Number").push(num)


        for i in range(len(result_text)):
            check_num(result_text[i])

            
    with col3:
        st.markdown('Web links')
        regex="\Ahttp"
        def check_url(web):   
            with st.spinner("Loading"):
                if(re.search(regex,web)):   
                    st.write(web)  
                    db.child("Web").push(web)

        for i in range(len(result_text)):
            check_url(result_text[i])
            


def hist():
    col1, col2, col3 = st.columns((1,1,1))

    with col1:
        st.markdown('Email')
        temp1 = db.child("Email").get().val()
        for i,j in enumerate(temp1):
            st.code(temp1[j])

    with col2:
        st.markdown('Number')
        temp2 = db.child("Number").get().val()
        for i,j in enumerate(temp2):
            st.code(temp2[j])

    with col3:
        st.markdown('Web')
        temp3 = db.child("Web").get().val()
        for i,j in enumerate(temp3):
            st.code(temp3[j])


if options=='Main':
    main_function()
if options=='History':
    hist()


