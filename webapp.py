from optparse import Option
import easyocr as ocr 
import streamlit as st
from PIL import Image
import numpy as np
import re   
import pyrebase
import datetime as datetime

    
# st.sidebar.title("Navigation")
# options=st.sidebar.radio('Pages', options=['Main','Sign in','History'])

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

# reader=load_model()  

global img
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
            # print(result_text)
        st.success("here you go!")
    else:
        st.write("Upload an image")
    
    db.child("results").push(result_text)

    col1, col2, col3 = st.columns((1,1,1))

    with col1:
        st.markdown('Email')
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  

        def check_mail(email):   
            with st.spinner("Loading"):
                if(re.search(regex,email)):   
                    st.write(email)  

        for i in range(len(result_text)):
            check_mail(result_text[i])

    with col2:
        st.markdown('Mobile')
        regex='^(\\+\\d{1,3}( )?)?((\\(\\d{1,3}\\))|\\d{1,3})[- .]?\\d{3,4}[- .]?\\d{4}$'
        def check_num(num):   
            with st.spinner("Loading"):
                if(re.search(regex,num)):   
                    st.write(num)  

        for i in range(len(result_text)):
            check_num(result_text[i])
            
    with col3:
        st.markdown('Web links')
        regex="\Ahttps"
        def check_url(web):   
            with st.spinner("Loading"):
                if(re.search(regex,web)):   
                    st.write(web)  

        for i in range(len(result_text)):
            check_url(result_text[i])
    return image
# def hist(img):
#     st.image(img)

# if options=='Main':
#     main()
# if options=='History':
#     hist(img)


def firebase_main():
    st.title("Welcome!")

    choice=st.selectbox('login/signup',('login','signup'))
    # choice = 'login'

    email = st.text_input("Email")
    password = st.text_input("password",type='password')

    if choice=='signup':
        handle=st.text_input('Handle name',value='Default')
        submit=st.button('Create my account')

        if submit:
            user=auth.create_user_with_email_and_password(email,password)
            st.success('Account created') 
            st.balloons()
            user=auth.sign_in_with_email_and_password(email,password)
            db.child(user['localID']).child("Handle").set(handle)
            db.child(user['localID']).child("ID").set(user['localID'])
            st.title("Welcome"+handle)

    if choice=='login':
        login=st.button('Continue')
        if login:
            user=auth.sign_in_with_email_and_password(email,password)
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            newImgPath=main_function()
            uid = user['localId']
            # Stored Initated Bucket in Firebase
            fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
            # Get the url for easy access
            a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
            # Put it in our real time database
            db.child(user['localId']).child("Image").push(a_imgdata_url)
            

firebase_main()


