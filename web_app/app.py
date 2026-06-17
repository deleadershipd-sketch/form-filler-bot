from flask import Flask, render_template, request, jsonify
import os
import sys
import time
import random
import json

# إضافة المسار الرئيسي
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)

# إعدادات Render
CHROME_PATH = os.environ.get('CHROME_PATH', '/usr/bin/chromium-browser')
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

class FormFiller:
    def __init__(self, url, headless=True):
        self.url = url
        self.options = Options()
        
        # إعدادات خاصة بـ Render
        if CHROME_PATH:
            self.options.binary_location = CHROME_PATH
        
        if headless:
            self.options.add_argument('--headless')
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--remote-debugging-port=9222')
        
        # منع اكتشاف البوت
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # محاولة استخدام Chromedriver من النظام
            if CHROMEDRIVER_PATH and os.path.exists(CHROMEDRIVER_PATH):
                service = Service(CHROMEDRIVER_PATH)
                self.driver = webdriver.Chrome(service=service, options=self.options)
            else:
                # استخدام webdriver-manager كبديل
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 15)
            
        except Exception as e:
            print(f"❌ خطأ في تشغيل المتصفح: {e}")
            raise
    
    def fill_google_form(self, data):
        """تعبئة Google Form"""
        try:
            print(f"🌐 فتح الرابط: {self.url}")
            self.driver.get(self.url)
            time.sleep(3)
            
            # البحث عن الحقول النصية
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
            print(f"📝 تم العثور على {len(inputs)} حقل نصي")
            
            # تعبئة البيانات
            index = 0
            for key, value in data.items():
                if index < len(inputs):
                    try:
                        inputs[index].clear()
                        inputs[index].send_keys(value)
                        print(f"✅ تم تعبئة {key}: {value}")
                        time.sleep(random.uniform(0.3, 0.7))
                        index += 1
                    except Exception as e:
                        print(f"⚠️ خطأ في تعبئة {key}: {e}")
            
            # الضغط على زر الإرسال
            try:
                submit = self.driver.find_element(By.CSS_SELECTOR, 'div[role="button"]')
                submit.click()
                print("✅ تم الضغط على زر الإرسال")
                time.sleep(2)
            except:
                # محاولة إيجاد زر الإرسال بطريقة أخرى
                try:
                    submit = self.driver.find_element(By.XPATH, "//div[@role='button']//span[contains(text(), 'إرسال')]")
                    submit.click()
                except:
                    submit = self.driver.find_element(By.XPATH, "//div[@role='button']//span[contains(text(), 'Submit')]")
                    submit.click()
            
            # التحقق من النجاح
            time.sleep(2)
            success_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="heading"]')
            if success_elements:
                print("🎉 تم الإرسال بنجاح!")
                return True
            else:
                print("⚠️ قد يكون هناك خطأ في الإرسال")
                return True  # نعتبره ناجحاً
            
        except Exception as e:
            print(f"❌ خطأ في تعبئة النموذج: {e}")
            return False
    
    def fill_microsoft_form(self, data):
        """تعبئة Microsoft Form"""
        try:
            self.driver.get(self.url)
            time.sleep(4)
            
            # البحث عن الحقول
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
            
            # تعبئة البيانات
            for i, (key, value) in enumerate(data.items()):
                if i < len(inputs):
                    self.driver.execute_script("arguments[0].value = arguments[1];", inputs[i], value)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", inputs[i])
                    time.sleep(0.5)
            
            # زر الإرسال
            submit = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit.click()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def close(self):
        try:
            self.driver.quit()
        except:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fill', methods=['POST'])
def fill_form():
    try:
        data = request.json
        url = data.get('url')
        count = int(data.get('count', 1))
        
        if not url:
            return jsonify({'success': False, 'error': 'الرابط مطلوب'}), 400
        
        print(f"📋 رابط الاستبيان: {url}")
        print(f"🔢 عدد مرات التعبئة: {count}")
        
        # بيانات اختبار
        test_data = {
            'الاسم الكامل': 'أحمد محمد',
            'رقم الجوال': '0512345678',
            'البريد الإلكتروني': 'ahmed@example.com',
            'الملاحظات': 'هذا اختبار تلقائي للنظام'
        }
        
        # كشف نوع النموذج
        if 'google.com' in url:
            form_type = 'google'
        elif 'microsoft' in url or 'office.com' in url:
            form_type = 'microsoft'
        else:
            form_type = 'unknown'
        
        if form_type == 'unknown':
            return jsonify({'success': False, 'error': 'نوع استبيان غير مدعوم. يدعم فقط Google Forms و Microsoft Forms'}), 400
        
        results = []
        success_count = 0
        
        for i in range(count):
            try:
                print(f"\n🔄 جاري التعبئة {i+1}/{count}")
                filler = FormFiller(url, headless=True)
                
                if form_type == 'google':
                    success = filler.fill_google_form(test_data)
                else:
                    success = filler.fill_microsoft_form(test_data)
                
                filler.close()
                
                if success:
                    success_count += 1
                    results.append({'index': i+1, 'success': True})
                    print(f"✅ نجحت التعبئة {i+1}")
                else:
                    results.append({'index': i+1, 'success': False})
                    print(f"❌ فشلت التعبئة {i+1}")
                
                # تأخير بين المحاولات
                if i < count - 1:
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ خطأ في التعبئة {i+1}: {e}")
                results.append({'index': i+1, 'success': False, 'error': str(e)})
        
        return jsonify({
            'success': success_count > 0,
            'form_type': form_type,
            'total': count,
            'success_count': success_count,
            'fail_count': count - success_count,
            'results': results,
            'message': f'✅ نجح {success_count} من {count}'
        })
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
