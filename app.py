from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# إنشاء مجلد الرفع إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# مفاتيح reCAPTCHA (استخدم المفاتيح التجريبية من Google أو مفاتيحك الخاصة)
RECAPTCHA_SITE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # مفتاح تجريبي
RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # مفتاح تجريبي

def verify_recaptcha(token):
    """التحقق من reCAPTCHA token"""
    if not token:
        return False
    
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': token
            }
        )
        result = response.json()
        return result.get('success', False)
    except:
        return False

def allowed_file(filename):
    """التحقق من امتداد الملف المسموح به"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    apps = db.relationship('App', backref='category', lazy=True)

class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='فارغ')
    image_url = db.Column(db.String(500), nullable=False)
    download_link = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    order = db.Column(db.Integer, default=0)

class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(200), default='𝐈𝐏𝐀 𝐌𝐀𝐉𝐑𝐀𝐌')
    primary_color = db.Column(db.String(20), default='#4a1a6b')
    accent_color = db.Column(db.String(20), default='#9b4dca')
    light_purple = db.Column(db.String(20), default='#7c3aed')
    background_start = db.Column(db.String(20), default='#1a0a2e')
    background_mid = db.Column(db.String(20), default='#16082d')
    background_end = db.Column(db.String(20), default='#0d051a')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    return settings

def get_social_links():
    return SocialLink.query.order_by(SocialLink.order).all()

@app.context_processor
def inject_settings():
    return dict(settings=get_settings(), social_links=get_social_links())

@app.template_filter('apply_colors')
def apply_colors_filter(css_content):
    settings = get_settings()
    css_content = css_content.replace('var(--bg-start)', settings.background_start)
    css_content = css_content.replace('var(--bg-mid)', settings.background_mid)
    css_content = css_content.replace('var(--bg-end)', settings.background_end)
    css_content = css_content.replace('var(--button-background-colo)', settings.primary_color)
    css_content = css_content.replace('var(--accent-glow)', settings.accent_color)
    css_content = css_content.replace('var(--light-purple)', settings.light_purple)
    return css_content

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/games')
def games():
    category = Category.query.filter_by(slug='games').first()
    apps = App.query.filter_by(category_id=category.id).order_by(App.order).all() if category else []
    return render_template('apps.html', apps=apps, page_title='العاب', category_slug='games')

@app.route('/applications')
def applications():
    category = Category.query.filter_by(slug='applications').first()
    apps = App.query.filter_by(category_id=category.id).order_by(App.order).all() if category else []
    return render_template('apps.html', apps=apps, page_title='تطبيقات', category_slug='applications')

@app.route('/all')
def all_apps():
    apps = App.query.order_by(App.order).all()
    return render_template('apps.html', apps=apps, page_title='الكل', category_slug='all')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    apps = []
    if query:
        apps = App.query.filter(App.name.contains(query)).all()
    return render_template('search.html', apps=apps, query=query)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/static/css/dynamic-style.css')
def dynamic_css():
    settings = get_settings()
    css_template = f"""
:root {{
    --child-background-color: #0a0014;
    --button-background-colo: {settings.primary_color};
    --accent-glow: {settings.accent_color};
    --light-purple: {settings.light_purple};
    --bg-start: {settings.background_start};
    --bg-mid: {settings.background_mid};
    --bg-end: {settings.background_end};
}}
"""
    return css_template, 200, {'Content-Type': 'text/css'}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        # التحقق من CAPTCHA أولاً
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            flash('فشل التحقق من أنك لست روبوت، حاول مرة أخرى', 'error')
            return render_template('admin/login.html')
        
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    apps_count = App.query.count()
    categories_count = Category.query.count()
    games_count = App.query.join(Category).filter(Category.slug == 'games').count()
    applications_count = App.query.join(Category).filter(Category.slug == 'applications').count()
    recent_apps = App.query.order_by(App.id.desc()).limit(5).all()
    return render_template('admin/dashboard.html', 
                          apps_count=apps_count, 
                          categories_count=categories_count,
                          games_count=games_count,
                          applications_count=applications_count,
                          recent_apps=recent_apps)

@app.route('/admin/features')
@login_required
def admin_features():
    return render_template('admin/features.html')

@app.route('/admin/apps')
@login_required
def admin_apps():
    apps = App.query.order_by(App.order).all()
    categories = Category.query.all()
    return render_template('admin/apps.html', apps=apps, categories=categories)

@app.route('/admin/upload-image', methods=['POST'])
@login_required
def upload_image():
    """رفع صورة وإرجاع رابطها"""
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم اختيار صورة'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار صورة'}), 400
    
    if file and allowed_file(file.filename):
        # إنشاء اسم ملف آمن مع طابع زمني
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # إرجاع الرابط المحلي للصورة
        image_url = url_for('static', filename=f'uploads/{filename}', _external=True)
        return jsonify({'success': True, 'url': image_url})
    
    return jsonify({'error': 'نوع الملف غير مسموح به. استخدم: png, jpg, jpeg, gif, webp'}), 400

@app.route('/admin/apps/add', methods=['POST'])
@login_required
def admin_add_app():
    name = request.form.get('name')
    description = request.form.get('description', 'فارغ')
    image_url = request.form.get('image_url')
    download_link = request.form.get('download_link')
    category_id = request.form.get('category_id')
    
    app_item = App(name=name, description=description, image_url=image_url, 
                   download_link=download_link, category_id=category_id)
    db.session.add(app_item)
    db.session.commit()
    flash('تمت إضافة التطبيق بنجاح', 'success')
    return redirect(url_for('admin_apps'))

@app.route('/admin/apps/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_app(id):
    app_item = App.query.get_or_404(id)
    app_item.name = request.form.get('name')
    app_item.description = request.form.get('description', 'فارغ')
    app_item.image_url = request.form.get('image_url')
    app_item.download_link = request.form.get('download_link')
    app_item.category_id = request.form.get('category_id')
    db.session.commit()
    flash('تم تعديل التطبيق بنجاح', 'success')
    return redirect(url_for('admin_apps'))

@app.route('/admin/apps/delete/<int:id>')
@login_required
def admin_delete_app(id):
    app_item = App.query.get_or_404(id)
    db.session.delete(app_item)
    db.session.commit()
    flash('تم حذف التطبيق', 'success')
    return redirect(url_for('admin_apps'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@login_required
def admin_add_category():
    name = request.form.get('name')
    slug = request.form.get('slug')
    category = Category(name=name, slug=slug)
    db.session.add(category)
    db.session.commit()
    flash('تمت إضافة القسم بنجاح', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:id>')
@login_required
def admin_delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('تم حذف القسم', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/social')
@login_required
def admin_social():
    links = SocialLink.query.order_by(SocialLink.order).all()
    return render_template('admin/social.html', links=links)

@app.route('/admin/social/add', methods=['POST'])
@login_required
def admin_add_social():
    name = request.form.get('name')
    url = request.form.get('url')
    icon = request.form.get('icon')
    link = SocialLink(name=name, url=url, icon=icon)
    db.session.add(link)
    db.session.commit()
    flash('تمت إضافة الرابط بنجاح', 'success')
    return redirect(url_for('admin_social'))

@app.route('/admin/social/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_social(id):
    link = SocialLink.query.get_or_404(id)
    link.name = request.form.get('name')
    link.url = request.form.get('url')
    link.icon = request.form.get('icon')
    db.session.commit()
    flash('تم تعديل الرابط بنجاح', 'success')
    return redirect(url_for('admin_social'))

@app.route('/admin/social/delete/<int:id>')
@login_required
def admin_delete_social(id):
    link = SocialLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    flash('تم حذف الرابط', 'success')
    return redirect(url_for('admin_social'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = get_settings()
    if request.method == 'POST':
        settings.site_title = request.form.get('site_title')
        settings.primary_color = request.form.get('primary_color')
        settings.accent_color = request.form.get('accent_color')
        settings.light_purple = request.form.get('light_purple')
        settings.background_start = request.form.get('background_start')
        settings.background_mid = request.form.get('background_mid')
        settings.background_end = request.form.get('background_end')
        db.session.commit()
        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html', settings=settings)

def init_db():
    with app.app_context():
        db.create_all()
        
        # تحديث أو إنشاء حساب المسؤول
        admin = User.query.first()
        if not admin:
            admin = User(username='majram', password=generate_password_hash('fgasdasd'))
            db.session.add(admin)
        else:
            admin.username = 'majram'
            admin.password = generate_password_hash('fgasdasd')
        
        if not Category.query.first():
            games = Category(name='العاب', slug='games')
            apps = Category(name='تطبيقات', slug='applications')
            db.session.add(games)
            db.session.add(apps)
        
        if not SocialLink.query.first():
            instagram = SocialLink(name='انستغرام', url='https://www.instagram.com/dr.atheistt', icon='2.png', order=1)
            telegram = SocialLink(name='تيليجرام', url='https://t.me/Lax_li', icon='1.png', order=2)
            tiktok = SocialLink(name='تيك توك', url='https://www.tiktok.com/@linksopranos', icon='4.png', order=3)
            db.session.add(instagram)
            db.session.add(telegram)
            db.session.add(tiktok)
        
        if not App.query.first():
            games_cat = Category.query.filter_by(slug='games').first()
            apps_cat = Category.query.filter_by(slug='applications').first()
            
            sample_apps = [
                App(name='PUBG MOBILE', description='ايم بوت ورادار ودعم لغه عربيه وانكليزيه والكثير', 
                    image_url='https://www6.0zz0.com/2023/12/29/02/235574676.png',
                    download_link='https://ipalinks.ru/wh/1QSoL', category_id=games_cat.id, order=1),
                App(name='Fortnite', description='فارغ', 
                    image_url='https://www12.0zz0.com/2023/12/29/02/923044524.png',
                    download_link='https://www.ipalinks.ru/dl/7BGpZNxj', category_id=games_cat.id, order=2),
                App(name='Among Us', description='فارغ', 
                    image_url='https://www10.0zz0.com/2024/04/10/13/242121755.jpeg',
                    download_link='https://www.ipalinks.ru/wh/34pKrz9CZM', category_id=games_cat.id, order=3),
                App(name='Roblox', description='فارغ', 
                    image_url='https://www8.0zz0.com/2024/04/10/13/289811710.png',
                    download_link='https://www.ipalinks.ru/wh/VkqgeuvH6', category_id=games_cat.id, order=4),
                App(name='Esign', description='تطبيق لتنزيل ملفات ipa لا يحتوي على شهاده', 
                    image_url='https://www7.0zz0.com/2023/12/29/02/616930548.png',
                    download_link='https://ipalinks.ru/wh/KsjN7g', category_id=apps_cat.id, order=1),
                App(name='سينمانا', description='تطبيق لمشاهده الافلام', 
                    image_url='https://www7.0zz0.com/2023/12/29/02/235834296.png',
                    download_link='https://www.ipalinks.ru/dl/qB4Mh1M7a', category_id=apps_cat.id, order=2),
                App(name='تيك توك', description='فارغ', 
                    image_url='https://www7.0zz0.com/2023/12/29/02/310788981.png',
                    download_link='https://www.ipalinks.ru/dl/yXjBq', category_id=apps_cat.id, order=3),
                App(name='صلاتك', description='تطبيق مدفوع على اب ستور بقيمه 9$', 
                    image_url='https://www8.0zz0.com/2024/04/10/13/383933872.png',
                    download_link='https://www.ipalinks.ru/wh/nJ23r45lA', category_id=apps_cat.id, order=4),
            ]
            for app_item in sample_apps:
                db.session.add(app_item)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
