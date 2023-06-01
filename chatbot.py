import random
import json
import pickle
import threading

import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

import os
import time

import speech_recognition as sr
import pyttsx3

import datetime  #pip install python-dateutil
from selenium.webdriver.common.keys import Keys
from selenium import webdriver             #pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from googletrans import Translator  #pip install googletrans==4.0.0-rc1

import smtplib
import wikipedia
import re
import math

from langdetect import detect
# setup giọng nói
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # set voice to English (US)
engine.setProperty('rate', 150)  # set speech rate
engine.setProperty('volume', 0.8)  # set speech volume

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Load data
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

#hàm tính xác suất câu trả lời
def get_accuracy(text):  # hàm tính xác suất
    intents_list = predict_class(text)
    if intents_list:  # kiểm tra nếu danh sách không rỗng
        intent = intents_list[0]['intent']
        probability = float(intents_list[0]['probability'])
        if intent == 'thanks':
            probability *= 0.8
        return probability
    else:  # xử lý nếu danh sách rỗng
        return 0.0  # hoặc giá trị khác tùy ý của bạn


#Hàm thời gian
def get_time(text):
    now = datetime.datetime.now()
    now1 = datetime.datetime.now().strftime("%w")
    now2 = int(now1)
    now3 = "Chủ Nhật"
    if "giờ" in text:
        return 'Bây giờ là %d giờ %d phút' % (now.hour, now.minute)
    elif "hôm nay" in text:
        return "Hôm nay là ngày %d tháng %d năm %d" %(now.day, now.month, now.year)
    elif "hôm qua" in text:
        return "Hôm qua là ngày %d tháng %d năm %d" % (now.day - 1, now.month, now.year)
    elif "ngày mai" in text:
        return "Ngày mai là ngày %d tháng %d năm %d" % (now.day + 1, now.month, now.year)
    elif "thứ" in text and now2!=0:
       return ('Hôm nay là thứ %s' % (now2+1))
    elif "thứ" in text and now2==0:
        return ('Hôm nay là %s' % (now3))
    else:
        return "Bot chưa hiểu ý của bạn."

#Hàm mở trình duyệt
def open_application(text):
    if "cốc cốc" in text:
        speak("Mở cốc cốc")
        os.startfile('browser.exe')
    elif "google" in text:
        speak("Mở google")
        os.startfile('chrome.exe')
    elif "excel" in text:
        speak("Mở Microsoft Excel")
        os.startfile('EXCEL.EXE')
    elif "word" in text:
        speak("Mở Microsoft Word")
        os.startfile('WINWORD.EXE')
    elif "powerpoint" in text:
        speak("Mở PowerPoint")
        os.startfile('POWERPNT.EXE')
    elif "notepad" in text or "ghi chú" in text:
        speak("Mở notepad")
        os.startfile('notepad.exe')
    else:
        speak("Ứng dụng chưa được cài đặt. Bạn hãy thử lại!")

#Mở và tìm kiếm
def open_google_and_search(text):
    search_for = text.split("kiếm", 1)[1]
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.get("http://www.google.com")
    que = driver.find_element(By.NAME, 'q')
    que.send_keys(str(search_for))
    que.send_keys(Keys.RETURN)
    time.sleep(100000)
    driver.quit()



#hàm Train
def doc_file():
    with open("intents.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = {k.lower():v for k,v in data.items()} # Chuyển đổi key của dictionary thành chữ thường
    for intent in data["intents"]:
        intent["tag"] = intent["tag"].lower() # Chuyển đổi tag thành chữ thường
        intent["patterns"] = [pattern.lower() for pattern in intent["patterns"]] # Chuyển đổi patterns thành chữ thường
        intent["responses"] = [response.lower() for response in intent["responses"]] # Chuyển đổi responses thành chữ thường
    return data

def train_bot(tag, new_patterns, new_responses):
    # Load dữ liệu từ file hiện tại
    data = doc_file()

    # Tìm intent có tag tương ứng
    for intent in data['intents']:
        if intent['tag'] == tag:
            # Nếu tìm thấy, cập nhật thêm thông tin mới vào intent
            intent['patterns'] = new_patterns
            intent['responses'] = new_responses
            break
    else:
        # Nếu không tìm thấy, tạo intent mới
        new_intent = {
            'tag': tag,
            'patterns': new_patterns,
            'responses': new_responses
        }
        data['intents'].append(new_intent)

    # Ghi lại dữ liệu vào file, sử dụng encoding 'utf-8'
    with open('intents.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4, separators=(", ", ": "))

def tag():
    data = doc_file()
    list_tag = []
    for intent in data["intents"]:
        list_tag.append(intent["tag"])
    return list_tag

def result_pa(tag):
    data = doc_file()
    pa = []
    for intent in data["intents"]:
        if intent["tag"] == tag:
            pa.append(intent["patterns"])
    return pa

def reslt_res(tag):
    data = doc_file()
    res = []
    for intent in data["intents"]:
        if intent["tag"] == tag:
            res.append(intent["responses"])
    return res




#thái , hàn , anh , nhật , trung ,pháp ,Đức , Ấn
def language_codes(text):
    if any(word in text for word in ["tiếng thái lan","tiếng thái","thái"]):
        lang = "th"
    elif any(word in text for word in ["tiếng hàn","tiếng hàn quốc","hàn"]):
        lang = "ko"
    elif any(word in text for word in ["tiếng anh","anh"]):
        lang = "en"
    elif any(word in text for word in ["tiếng nhật","tiếng nhật bản","nhật bản"]):
        lang = "ja"
    elif any(word in text for word in ["tiếng trung","tiếng trung quốc","trung quốc"]):
        lang = "zh"
    elif any(word in text for word in ["tiếng pháp", "pháp"]):
        lang = "fr"
    elif any(word in text for word in ["tiếng đức", "đức"]):
        lang = "de"
    elif any(word in text for word in ["tiếng ấn", "ấn độ","ấn"]):
        lang = "de"
    else :
        lang = "không phát hiện ngôn ngữ"
    return lang

def trans(text):
    translator = Translator()
    result = translator.translate(text, src='en', dest="vi")
    # Trả về kết quả
    return result.text

#Hàm dịch
def translate(text):
    # Tạo đối tượng Translator
    translator = Translator()
    if "sang" in text:
        parts = text.split(":")
        parts = parts[1].split("sang")
        source = "vi"
        target = "en"
        if len(parts) < 2:
            return "Bạn vui lòng nhập đúng cú pháp: \"dịch : [từ cần dịch] sang tiếng anh\". Ví dụ: \"nghĩa của từ : xin chào sang tiếng anh\"."
        text_to_translate = parts[0].strip()  # Lấy phần chuỗi cần dịch, loại bỏ khoảng trắng
        # Dịch văn bản
        result = translator.translate(text_to_translate, src=source, dest=target)
        # Trả về kết quả
        return result.text
    else:
        target = "vi"
        parts = text.split(":")
        lang = text.split(":")[1]
        source = detect(lang)
        if len(parts) < 2:
            return "Bạn vui lòng nhập đúng cú pháp: \"nghĩa của từ : [từ cần dịch]\". Ví dụ: \"nghĩa của từ : hello\"."
        text_to_translate = parts[1].strip()  # Lấy phần chuỗi cần dịch, loại bỏ khoảng trắng
        # Dịch văn bản
        result = translator.translate(text_to_translate, src=source, dest=target)
        # Trả về kết quả
        return result.text

#Hàm tính toán
def giai_phuong_trinh_bac_nhat(phuong_trinh):
    pattern = r"([+-]?\d*\.?\d+)x\s*([+-])\s*(\d*\.?\d+)\s*=\s*0"
    match = re.match(pattern, phuong_trinh)
    if match:
        a = float(match.group(1))
        b = float(match.group(3))
        if match.group(2) == "+":
            x = -b/a
        else:
            x = b/a
        return "Kết quả x= " + str(x)
    else:
        raise ValueError("Phương trình không hợp lệ. Nếu x + 1 = 0 thì thay bằng 1x + 1 = 0")

def giai_phuong_trinh_bac_hai(phuong_trinh):
    # Tìm các hệ số trong phương trình bậc 2
    pattern = r"(-?\d*\.?\d*)?x\^2\s*([+-])\s*(\d*\.?\d*)?x\s*([+-])\s*(\d*\.?\d*)\s*=\s*0"
    match = re.match(pattern, phuong_trinh)

    if match:
        a_sign = "-" if match.group(1) and match.group(1)[0] == "-" else "+"
        a_value = match.group(1)[1:] if match.group(1) else "1"
        if a_value == ".":
            a_value = "0" + a_value
        a = float(a_sign + a_value)

        b_sign = match.group(2)
        b_value = match.group(3)
        if b_sign == "-":
            b_value = "-" + b_value
        b = float(b_value) if b_value else 0

        c_sign = match.group(4) if match.group(4) else "+"
        c_value = match.group(5) if match.group(5) else "0"

        if c_value == ".":
            c_value = "0" + c_value
        c = float(c_sign + c_value)

        # Tính delta
        delta = b**2 - 4*a*c
        # Xử lý các trường hợp của delta
        if delta > 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            return "Kết quả : x1 = " + str(x1) + ", x2 = " + str(x2)
        elif delta == 0:
            x = -b/(2*a)
            return "Kết quả : x = " + str(x)
        else:
            x_real = -b / (2 * a)
            x_imag = math.sqrt(-delta) / (2 * a)
            return "Vô nghiệm : x1 = {} + {}i".format(x_real, x_imag).replace("'", ""), "x2 = {} - {}j".format(x_real, x_imag).replace("'", "")
    else:
        raise ValueError("Phương trình không hợp lệ.")

def tinhtoan(text):
    try:
        if "x^2" in text:
            if ":" in text:
                equation = text.split(":")[1].strip()
                return giai_phuong_trinh_bac_hai(equation)
            else:
                return giai_phuong_trinh_bac_hai(text)
        if "x" in text:
            if ":" in text:
                equation = text.split(":")[1].strip()
                return giai_phuong_trinh_bac_nhat(equation)
            else:
                return giai_phuong_trinh_bac_nhat(text)

        if "bằng" in text:
            text = text.replace("bằng","=")
        if "^" in text:
            text = text.replace("^","**")
        if "cộng" in text:
            text = text.replace("cộng","+")
        if "trừ" in text:
            text = text.replace("trừ","-")
        if "nhân" in text:
            text = text.replace("nhân","*")
        if "chia" in text:
            text = text.replace("chia","/")
        if "mũ" in text:
            text = text.replace("mũ","**")

        equation = text.split("=")[0]
        # Kiểm tra cú pháp phép tính
        if not any(char.isdigit() for char in equation):
            return "Không tìm thấy phép tính."
        # Tính kết quả phép tính
        result = eval(equation)
        # Trả về kết quả
        return "Kết quả = " + str(result)
    except:
        return "Không thể tính toán phép tính."




def wiki(text):
    try:
        if ":" in text:
            text = text.split(":")[1]
            search_results = wikipedia.summary(text)
            return search_results
        else:
            return "Bạn vui lòng gõ đúng cú pháp: Định nghĩa : {từ cần định nghĩa}"
    except wikipedia.exceptions.DisambiguationError as e:
        # Xử lý khi có nhiều kết quả tìm kiếm
        options = e.options
        return "Có nhiều kết quả phù hợp. Vui lòng cung cấp thêm thông tin cụ thể hoặc chọn một kết quả: {}".format(options)
    except wikipedia.exceptions.PageError:
        # Xử lý khi không tìm thấy trang
        return "Không tìm thấy thông tin về '{}'".format(text)
    except:
        # Xử lý các lỗi khác
        return "Bot không thể truy cập Wikipedia lúc này. Xin lỗi vì sự bất tiện này."


def login_to_website(username, password , text):

    # Khởi tạo trình duyệt web
    service = webdriver.chrome.service.Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # Mở trang web
    driver.get('http://qldt.tgu.edu.vn/login')

    # Tìm và nhập thông tin đăng nhập
    username_input = driver.find_element(By.ID, 'txt_Login_ten_dang_nhap')
    password_input = driver.find_element(By.ID, 'pw_Login_mat_khau')

    username_input.send_keys(username)
    password_input.send_keys(password)

    # Tìm nút đăng nhập và chờ cho đến khi nó xuất hiện
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'bt_Login_submit'))
    )

    # Click nút đăng nhập
    login_button.click()
    if "lịch thi" in text:
        driver.get("http://qldt.tgu.edu.vn/sinhvien/lichthi/xemlichthicanhan")
    if "đăng ký học phần" in text:
        driver.get("http://qldt.tgu.edu.vn/sinhvien/dangkyhocphan/dangky")
    if "điểm" in text:
        driver.get("http://qldt.tgu.edu.vn/sinhvien/diem/xemketquahoctap")
    if "kế hoạch học tập" in text:
        driver.get("http://qldt.tgu.edu.vn/sinhvien/kehoach/xemctdtkehoach")
    if "học phí" in text:
        driver.get("http://qldt.tgu.edu.vn/sinhvien/thuhocphi/thuhocphisv")
    # Sau khi đăng nhập thành công, bạn có thể thực hiện các tác vụ khác trên trang web.
    time.sleep(100000)

    # Đóng trình duyệt
    driver.quit()



#CHATBOT
def chatbot(text):
    try:
        text = text.lower()
        xs = get_accuracy(text)
        if any(word in text for word in ["mấy giờ", "là ngày mấy","thứ mấy" , "ngày mai là ngày nào" ,"hôm nay là ngày mấy" ,"ngày mai là ngày nào" ,"ngày mai là ngày mấy" ,"hôm nay là ngày nào" ,"hôm qua là ngày mấy","hôm nay là thứ mấy"]):
            return get_time(text)

        if any(word in text for word in ["mở"]):
            if any(word in text for word in ["tìm","tra cứu","search"]):
                search_thread = threading.Thread(target=open_google_and_search, args=(text,))
                search_thread.start()
                return "Mở google và tìm kiếm"
            else:
                open_application(text)
                return text + " thành công !"
        if any(word in text for word in ["nghĩa của","dịch","chuyển câu"]):
            return translate(text)
        if any(word in text for word in ["định nghĩa"]):
            return translate(wiki(text))
        if any(word in text for word in ["quản lý đào tạo","xem điểm", "xem lịch thi" , "xem thời khóa biểu" , "lập kế hoạch học tập" , "đóng tiền" , "học phí"]):
            search_thread = threading.Thread(target=login_to_website, args=("020101051", "01678373822aA", text))
            search_thread.start()
            return "Mở website thành công"
        if any(word in text for word in ["thực hiện phép toán" , "=" , "bằng mấy","phương trình bậc nhất","phương trình bậc 2" ,"x^2" , "tìm x"]):
            return str(tinhtoan(text))

        elif xs >= 0.8:
            ints = predict_class(text)
            res = get_response(ints, intents)
            robot_brain = res
            return robot_brain
        else:
            return "Xin lỗi, tôi không biết câu trả lời."

    except sr.RequestError:
        return "Xin lỗi, tôi không thể kết nối tới Google Speech Recognition service!"

