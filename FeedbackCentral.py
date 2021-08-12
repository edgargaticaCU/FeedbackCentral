
from flask import Flask, request
import sqlalchemy
import json
import os

app = Flask(__name__)
SECRET_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD', None)
assert SECRET_PASSWORD
url = sqlalchemy.engine.url.URL.create(
        drivername="mysql+pymysql",
        username='edgar',
        password=SECRET_PASSWORD,
        database='text_mined_assertions',
        query={
            "unix_socket": "/cloudsql/lithe-vault-265816:us-central1:text-mined-assertions-stage"
        }
)
engine = sqlalchemy.create_engine(url)


@app.route('/')
def nope():
    return 'service is running'


@app.route('/test')
def some_data():
    result_string = 'TEST:'
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text('SELECT * FROM text_mined_assertions.assertion'))
        for row in result:
            result_string = result_string + str(row)
    return result_string


@app.route('/evaluations', methods=['POST'])
def create_evaluation():
    if request.is_json:
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
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text(sql_statement))
        return 'Evaluation saved', 200
    return 'Not a JSON request', 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
