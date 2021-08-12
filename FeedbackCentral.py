from flask import Flask, request
from flaskext.mysql import MySQL
from google.cloud import secretmanager
import json

app = Flask(__name__)
mysql = MySQL()
client = secretmanager.SecretManagerServiceClient()
secret_response = client.access_secret_version(request={"name": "projects/575571346320/secrets/EdgarMySQLPassword/versions/1"})
app.config['MYSQL_DATABASE_USER'] = 'edgar'
app.config['MYSQL_DATABASE_PASSWORD'] = secret_response.payload.data.decode("UTF-8")
app.config['MYSQL_DATABASE_DB'] = 'text_mined_assertions'
app.config['MYSQL_DATABASE_HOST'] = '34.69.18.127'
mysql.init_app(app)

@app.route('/')
def nope():
    return 'service is running'


@app.route('/test')
def some_data():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM text_mined_assertions.assertion;')
    data = cursor.fetchall()
    return str(data)


@app.route('/evaluations', methods=['POST'])
def create_evaluation():
    if request.is_json:
        conn = mysql.connect()
        cursor = conn.cursor()
        request_dict = json.loads(request.data)
        if 'assertion_id' not in request_dict:
            return 'No assertion_id present in request', 400
        column_list = ['assertion_id', 'overall_correct']
        value_list = ['"' + request_dict['assertion_id'] + '"', '0']  # if the only info is the ID we assume it is being marked as incorrect.
        if 'overall_correct' in request_dict:
            value_list[1] = str(int(request_dict['overall_correct']))
        if 'subject_correct' in request_dict:
            column_list.append('subject_correct')
            value_list.append(str(int(request_dict['subject_correct'])))
        if 'object_correct' in request_dict:
            column_list.append('object_correct')
            value_list.append(str(int(request_dict['object_correct'])))
        if 'predicate_correct' in request_dict:
            column_list.append('predicate_correct')
            value_list.append(str(int(request_dict['predicate_correct'])))
        sql_statement = f"INSERT INTO text_mined_assertions.evaluation ({','.join(column_list)}) VALUES({','.join(value_list)})"
        cursor.execute(sql_statement)
        conn.commit()
        cursor.close()
        return 'Evaluation saved', 200
    return 'Not a JSON request', 400
