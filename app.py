from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

###########################################
# データベースの初期化
def init_db():
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS project_info (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			project_name TEXT NOT NULL,
			created_at TEXT NOT NULL,
			updated_at TEXT NOT NULL
		)
	''')
	conn.commit()
	conn.close()

# プロジェクト一覧を取得する関数
def get_project_info():
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	cursor.execute('SELECT id, project_name, created_at, updated_at FROM project_info')
	project_info = cursor.fetchall()
	conn.close()
	return project_info

# トップページを表示
@app.route('/')
def index():
	project_info = get_project_info()
	return render_template('index.html', project_info=project_info)

#############################################
# プロジェクトごとにデータベースファイルを作成する関数
def create_project_folder(project_name):
	db_folder_path = f'database/{project_name}'
	os.makedirs(db_folder_path, exist_ok=True)

# プロジェクトごとにテーブルを作成する関数
def create_project_table(project_name, columns):
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# テーブルを作成
	column_definitions = ', '.join([f'"{column}" TEXT' for column in columns])
	cursor.execute(f'''
		CREATE TABLE IF NOT EXISTS {project_name} (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			{column_definitions}
		)
	''')
	conn.commit()
	conn.close()

# プロジェクト情報をプロジェクト情報テーブルに保存する関数
def save_project_info(project_name):
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	cursor.execute('''
		INSERT INTO project_info (project_name, created_at, updated_at)
		VALUES (?, ?, ?)
	''', (project_name, now, now))
	conn.commit()
	conn.close()

# プロジェクト登録画面を表示
@app.route('/project-register', methods=['GET', 'POST'])
def project_register():
	if request.method == 'POST':
		project_name = request.form.get('project-name')
		item_names = request.form.getlist('item-name')

		create_project_folder(project_name)
		create_project_table(project_name, item_names)
		save_project_info(project_name)

		return redirect(url_for("index"))
	return render_template('project_register.html')

#################################
# プロジェクトに画像データを取得する関数
def get_project_detail(id):
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	cursor.execute('SELECT id, project_name, created_at, updated_at FROM project_info WHERE id = ?', (id,))
	project_info = cursor.fetchone()
	conn.close()
	return project_info

# テーブルのヘッダー項目を取得する関数
def get_table_headers(project_name):
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	cursor.execute('PRAGMA table_info({})'.format(project_name))
	headers = cursor.fetchall()
	conn.close()
	return [header[1] for header in headers if header[1] != 'id']

def update_last_modified_time(data_id):
	conn = sqlite3.connect('database/project_info.db')
	cursor = conn.cursor()
	current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	cursor.execute("UPDATE project_info SET updated_at=? WHERE id=?", (current_time, data_id))
	conn.commit()
	conn.close()

# 画像を保存する関数
def save_image(image_file, project_folder, data_id):
	image_filename = f"{data_id}.png"
	image_path = os.path.join(project_folder, image_filename)
	image_file.save(image_path)

	update_last_modified_time(data_id)

# テーブルにテキストデータを保存する関数
def save_text_data(project_name, text_data):
	db_path = 'database/project_info.db'
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# テキストデータを挿入するためのSQL文を作成
	columns = ', '.join(text_data.keys())
	placeholders = ', '.join(['?'] * len(text_data))
	values = tuple(text_data.values())

	# テキストデータを挿入する
	cursor.execute(f'''
		INSERT INTO {project_name} ({columns})
		VALUES ({placeholders})
	''', values)

	last_row_id = cursor.lastrowid    # 挿入したデータのIDを取得
	conn.commit()
	conn.close()
	return last_row_id  # 挿入したデータのIDを返す

# プロジェクトの詳細ページを表示
@app.route('/project_detail/<project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
	project_info = get_project_detail(project_id)
	if not project_info:
		return '指定されたプロジェクトが見つかりませんでした。', 404

	if request.method == "POST":
		# テキスト入力のデータを保存する処理
		text_data = {}
		all_empty = True
		for header in get_table_headers(project_info[1]):
			if header in request.form:
				text_data[header] = request.form[header]
				if request.form[header]:
					all_empty = False
		if all_empty:
			redirect("project_detail")
		else:
			data_id = save_text_data(project_info[1], text_data)

			if 'image' in request.files:
				image_file = request.files['image']
				if image_file.filename != '':
					# プロジェクト名に対応するフォルダを作成する
					project_name = project_info[1]
					project_folder = os.path.join('database', project_name)
					save_image(image_file, project_folder, data_id)
			return redirect(url_for("index"))

	table_headers = get_table_headers(project_info[1])  # プロジェクト名を使ってヘッダーを取得
	return render_template('project_detail.html', project_info=project_info, table_headers=table_headers)

######################################
# プロジェクトで保存した画像を表示
@app.route('/project_images/<project_id>', methods=['GET', 'POST'])
def project_images(project_id):
	project_info = get_project_detail(project_id)
	if not project_info:
		return '指定されたプロジェクトが見つかりませんでした。', 404

	project_name = project_info[1]
	project_folder = os.path.join('database', project_name)
	if not os.path.exists(project_folder):
		return 'プロジェクトフォルダが見つかりませんでした。', 404

	all_images = [f for f in os.listdir(project_folder) if os.path.isfile(os.path.join(project_folder, f)) and f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]

	project_info = get_project_detail(project_id)
	table_headers = get_table_headers(project_info[1])
	if request.method == "POST":
		search_criteria = {header: request.form.get(header) for header in get_table_headers(project_info[1]) if request.form.get(header)}
		if search_criteria:
			conn = sqlite3.connect('database/project_info.db')
			cursor = conn.cursor()
			query = f"SELECT id FROM {project_name} WHERE " + " AND ".join([f"{header} = ?" for header in search_criteria.keys()])
			cursor.execute(query, tuple(search_criteria.values()))
			matching_ids = [str(row[0]) for row in cursor.fetchall()]
			conn.close()
			images = [img for img in all_images if any(img.startswith(id) for id in matching_ids)]
		else:
			images = all_images
		print("----------------------\n", request.form)
		for header in table_headers:
			print("テスト：", request.form.get(header))
	else:
		images = all_images

	return render_template('project_images.html', project_info=project_info, images=images, table_headers=table_headers)

@app.route('/database/<path:filename>')
def serve_image(filename):
	return send_from_directory('database', filename)

###############################
if __name__ == '__main__':
	init_db()	# データベースの初期化
	app.run(debug=True)
