from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from contact.models import contactform
import nltk
from nltk.corpus import stopwords

from nltk.stem import PorterStemmer
import pickle

@login_required(login_url="/login")
def home(request):
    """
    @brief this the main view function which gives access to the home page
    @details to access this page a login check is made which is set as required field and the spam detection algorithms are present in this view function which takes the raw message from the input field and performs the data preprocessing and passes the processed data through the machine learning algorithms and gives a binary output which defines whether it is a spam or ham message
    @param request: it requests the index.html and passes the message object
    """
    if request.method=="POST":

        if request.FILES == '':
            msg = "choose a file to upload"
            return render(request,'index.html',{'message':msg})

        else:
         uploaded_text = request.POST.get('rawtext')
         #data preprocessing
         ps = PorterStemmer()

         def transform_text(text):
            text = text.lower()
            text = nltk.word_tokenize(text)
            y = []
            for i in text:
                if i.isalnum():
                    y.append(i)

            text = y[:]
            y.clear()

            for i in text:
                if i not in stopwords.words('english') and i not in string.punctuation:
                    y.append(i)
                    
            text = y[:]
            y.clear()
            for i in text:
                y.append(ps.stem(i))
                
            return " ".join(y)

        processed_text =[transform_text(uploaded_text)]
        print(processed_text)

        tfid_path = "static/spam_models/tfidf1.pkl" #vectorizer
        with open(tfid_path, 'rb') as f:
            tfid = pickle.load(f)

        if not isinstance(tfid, TfidfVectorizer):
            raise TypeError("The loaded object is not a TfidfVectorizer")

        matriz_text = tfid.transform(processed_text)
        print(matriz_text)
        final_text = matriz_text.toarray()

        ABC_path = "static/spam_models/AdaBoostClassifier.pkl"
        KNN_path = "static/spam_models/KNeighborsClassifier.pkl"
        LC_path = "static/spam_models/LogisticRegression.pkl"
        MNB_path = "static/spam_models/MultinomialNB.pkl"
        SVC_path = "static/spam_models/SVC.pkl"

        with open(ABC_path , 'rb') as a:
            ABC = pickle.load(a)

        with open(KNN_path , 'rb') as b:
            KNN = pickle.load(b)    
        
        with open(LC_path , 'rb') as c:
            LC = pickle.load(c)

        with open(MNB_path , 'rb') as d:
            MNB = pickle.load(d)

        with open(SVC_path , 'rb') as e:
            SVC = pickle.load(e)


        abc_result = ABC.predict(final_text)
        if abc_result == 1:
           abc_transaction = 'SPAM'
        else:
            abc_transaction = 'HAM'

        knn_result = KNN.predict(final_text)
        if knn_result == 1:
           knn_transaction = 'SPAM'
        else:
            knn_transaction = 'HAM'

        lc_result = LC.predict(final_text)
        if lc_result == 1:
           lc_transaction = 'SPAM'
        else:
            lc_transaction = 'HAM'
        
        mnb_result = MNB.predict(final_text)
        if mnb_result == 1:
           mnb_transaction = 'SPAM'
        else:
            mnb_transaction = 'HAM'

        svc_result = SVC.predict(final_text)
        if svc_result == 1:
           svc_transaction = 'SPAM'
        else:
            svc_transaction = 'HAM'
        
        model_names = ["Ada Boost Classifier", "K Neighbors Classifier", "Logistic Regression", "Multinomial NB","Support Vector Classifier"]
        #{'dc_prediction':dc_transaction, 'knn_prediction':knn_transaction, 'lc_prediction':lc_transaction, 'mnb_prediction':mnb_transaction, 'svc_prediction':svc_transaction,}
        return render(request, 'home.html', {'abc_prediction':abc_transaction, 'knn_prediction':knn_transaction, 'lc_prediction':lc_transaction, 'mnb_prediction':mnb_transaction, 'svc_prediction':svc_transaction, 'models':model_names})

    return render(request, 'home.html')  

def models(request):
    """
    @brief this the machine learning models view function which renders models.html
    @details in this it renders the models.html page which contains all the data about the models used for spam detection
    @param request: it requests the models.html 
    """
    return render(request,'models.html')

def contact(request):
    """
    @brief this the contact us view function which renders contact.html
    @details in this it renders the contact.html page which takes form input and saves the data into database named contactform  
    @param request: it requests the contact.html 
    """
    if request.method == "POST":
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        text = request.POST.get('message')
        en = contactform(name=name,email=email,message=text)
        en.save()

    return render(request,'contact.html')     

def signup(request):
     """
    @brief this is the signup view function which renders signup.html
    @details in this it renders the signup.html page which takes form input and saves the data into database named admin  
    @param request: it requests the signup.html 
    """
     if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            else:   
                user = User.objects.create_user(username=username, password=password1, email=email,first_name=first_name,last_name=last_name)
                user.save()
                print('user created')
                return redirect('login')
        else:
            messages.info(request,'password not matching..')    
            return redirect('signup')
     else:
        return render(request, 'signup.html')

def login(request):
    """
    @brief this is the signup view function which renders login.html
    @details in this it renders the login.html page which takes form input and fetchs the credentials and validates the details  
    @param request: it requests the login.html 
    """
    if request.method== 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request,'invalid credentials')
            return redirect('login')
    else:

        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('login') 

