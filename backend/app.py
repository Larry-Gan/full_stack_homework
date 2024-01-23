from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import json
import os
import zipfile

app = Flask(__name__)

# Database connection details
app.config.from_mapping(
    DB_HOST = os.environ.get('DB_HOST', 'localhost'),
    DB_USER = os.environ.get('DB_USER', 'root'),
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mysecretpassword'),
    DB_DATABASE = os.environ.get('DB_DATABASE', 'machina_labs')
)

CORS(app)

@app.route('/directory', methods=['GET'])
def directory():
    # Connect to the database
    try:
        db = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_DATABASE']
        )
        cursor = db.cursor(dictionary=True)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return jsonify({'Error connecting to the database: ': str(e)}), 500

    # Query the entire db
    query = """
        SELECT 
            c.name AS customer_name, 
            p.name AS part_name, 
            pr.name AS revision_name, 
            pr.uuid AS revision_uuid,
            pr.geometry_file_uuid AS cad_file_uuid,
            cadf.type AS cad_file_type,
            cadf.location AS cad_file_location,
            t.uuid AS trial_uuid, 
            pru.type AS process_run_type,
            f.uuid AS file_uuid, 
            f.type AS file_type, 
            f.location AS file_location
        FROM customer c
        JOIN part p ON c.uuid = p.customer_uuid
        JOIN part_revision pr ON p.uuid = pr.part_uuid
        LEFT JOIN file cadf ON pr.geometry_file_uuid = cadf.uuid
        LEFT JOIN trial t ON pr.uuid = t.part_revision_uuid
        LEFT JOIN process_run pru ON t.uuid = pru.trial_uuid
        LEFT JOIN process_run_file_artifact prfa ON pru.uuid = prfa.process_run_uuid
        LEFT JOIN file f ON prfa.file_artifact_uuid = f.uuid
        ORDER BY c.name, p.name, pr.name, t.uuid, pru.type, f.uuid;
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        # Organizing data 
        data = {}
        for row in rows:
            customer = row['customer_name']
            part = row['part_name']
            revision = row['revision_name']
            cad_file_uuid = row['cad_file_uuid']
            cad_file_type = row['cad_file_type']
            cad_file_location = row['cad_file_location']
            trial = row['trial_uuid']
            process_run_type = row['process_run_type']
            file_uuid = row['file_uuid']
            file_type = row['file_type']
            file_location = row['file_location']

            # Delete duplicates
            if customer not in data:
                data[customer] = {}
            if part not in data[customer]:
                data[customer][part] = {}
            if revision not in data[customer][part]:
                data[customer][part][revision] = {
                    "CAD": [] if cad_file_uuid else None,
                    "Trials": {}
                }

            # Add CAD file to revision
            if cad_file_uuid and {
                "uuid": cad_file_uuid,
                "type": cad_file_type,
                "location": cad_file_location,
                "name": cad_file_location.split("/")[-1]
            } not in data[customer][part][revision]["CAD"]:
                data[customer][part][revision]["CAD"].append({
                    "uuid": cad_file_uuid,
                    "type": cad_file_type,
                    "location": cad_file_location,
                    "name": cad_file_location.split("/")[-1]
                })

            # Add file to trial and categorize by process_run_type
            if trial and file_uuid:
                file = {
                    "uuid": file_uuid,
                    "type": file_type,
                    "location": file_location,
                    "name": file_location.split("/")[-1]
                }
                if process_run_type not in data[customer][part][revision]["Trials"]:
                    data[customer][part][revision]["Trials"][process_run_type] = []
                if file not in data[customer][part][revision]["Trials"][process_run_type]:
                    data[customer][part][revision]["Trials"][process_run_type].append(file)

        json_data = json.dumps(data, indent=4)
        print(json_data)
        return json_data

    except Exception as e:
        print(f"Error executing query: {e}")
        return jsonify({'Error executing query: ': str(e)}), 500

    finally:
        cursor.close()
        db.close()

@app.route('/file_preview', methods=['GET'])
def file_preview():
    # Get file location
    file_location = os.path.join("files/", request.args.get('location'))
    zip_file_path = './files.zip' 

    # Read file from zip as plaintext and return content
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            with z.open(file_location) as file:
                content = file.read().decode('utf-8') 
                return jsonify({'content': content}), 200
    except KeyError:
        return jsonify({'error': 'File not found in zip archive'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/file_download', methods=['GET'])
def file_download():
    # Get file location
    file_location = os.path.join("files/", request.args.get('location'))
    zip_file_path = './files.zip' 

    # Read file from zip and send file to Frontend for download
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            if file_location in z.namelist():
                temp_path = z.extract(file_location)
                return send_file(temp_path, as_attachment=True)
            else:
                return jsonify({'error': 'File does not exist in zip archive'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

if __name__ == '__main__':
    app.run(debug=True)
