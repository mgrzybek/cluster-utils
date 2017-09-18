from flask import Flask
import json, subprocess
app = Flask(__name__)

@app.route("/run")
def run_shell():
	lines = subprocess.check_output("/bin/ls").split('\n')
	return json.dumps(lines)
	

