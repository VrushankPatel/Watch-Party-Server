from flask import Flask, request, Response, jsonify
import os, re
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})

currentSeek = 0

@app.after_request
def postRequest(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def getChunk(movieName, chunkByte1=None, chunkByte2=None):
    blobUrl = "movies/" + movieName
    blobSize = os.stat(blobUrl).st_size
    start = 0
    
    if chunkByte1 < blobSize:
        start = chunkByte1    
    length = chunkByte2 + 1 - chunkByte1 if chunkByte2 else blobSize - start    

    with open(blobUrl, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, blobSize


@app.route('/video/<movieName>')
def getBlob(movieName):
    
    range = request.headers.get('Range', None)    
    chunkByte1, chunkByte2 = 0, None
    if range:
        match = re.search(r'(\d+)-(\d*)', range)
        groups = match.groups()
        if groups[0]:
            chunkByte1 = int(groups[0])
        if groups[1]:
            chunkByte2 = int(groups[1])        
       
    chunk, start, length, file_size = getChunk(movieName, chunkByte1, chunkByte2)
    response = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
    response.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))  
    return response

@app.route("/seekTo")
def seekedValue():
    global currentSeek
    currentSeek = int(request.args.get('seekTo'))
    return jsonify({"seekedTo" : currentSeek})

@app.route("/currentSeek")
def currentDeekedValue():
    global currentSeek    
    return jsonify({"currentSeek" : currentSeek})

@app.route("/moviesList")
def getAvailableMovies():
    moviesList = {"moviesList" : os.listdir("movies/")}
    return jsonify(moviesList)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)