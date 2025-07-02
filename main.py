from flask import render_template, Flask, request, jsonify, Response
from inference import *  # noqa: F403
from PIL import Image
import zipfile
import io
from tqdm import tqdm
from stats import *  # noqa: F403
import base64
import uuid
import threading
import time
import logging 
import json

app = Flask(__name__)

progress_dict = {}
logging.basicConfig(filename="logger.log", level=logging.DEBUG)  # or INFO, WARNING, etc.
logger = logging.getLogger(__name__)

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/infer', methods=["POST"])
def infer_images():
    logger.info("received")
    imgs = request.files["images"]
    file_buffer = io.BytesIO(imgs.read())
    content_type = imgs.content_type
    try:
        name = request.files["name"]
    except:  # noqa: E722
        name = "images"

    job = str(uuid.uuid4())
    progress_dict[job] = {"status": "starting"}

    logger.error("done receiving")

    def background_job(file_buffer, content_type, name, job):
        logger.error("started")
        zip_mem = io.BytesIO()
        zipf = zipfile.ZipFile(zip_mem, "w")
        if "zip" in content_type:

            content_bytes = io.BytesIO(file_buffer.read())
            content = zipfile.ZipFile(content_bytes, 'r')
            total = len(content.namelist())

            low, mid, high = 0, 0, 0
            
            for i, img_name in (enumerate(content.namelist())):
                logger.info(i)
                mask = infer(Image.open(io.BytesIO(content.read(img_name))))  # noqa: F405
                progress_dict[job] = {"status": "inference-done", "percent" : f"{(i + 0.5)/total*100:.2f}"}
                logger.info("1")
                results = get_percents(mask)  # noqa: F405
                logger.info("2")
                low += results["low"]
                mid += results["mid"]
                high += results["high"]
                
                mask_b = io.BytesIO()
                mask.save(mask_b, format="PNG")
                mask_b.seek(0)
            
                zipf.writestr(img_name, mask_b.read())
                
                progress_dict[job] = {"status": "inference-done", "percent" : f"{(i + 1)/total*100:.2f}"}
                logger.info("3")
            results = {
                "low": low/len(content.namelist()),
                "mid": mid/len(content.namelist()),
                "high": high/len(content.namelist())
                }

        else:
            logger.info(file_buffer)
            mask=infer(img=Image.open(file_buffer))  # noqa: F405
            logger.info("1")
            progress_dict[job] ={"status": "inference-done", "percent": "50"}
            
            results = get_percents(mask)  # noqa: F405
            logger.info("2")

            mask_b = io.BytesIO()
            mask.save(mask_b, format="PNG")
            mask_b.seek(0)
            
            zipf.writestr(f"{name}.PNG", mask_b.read())  
        
        zipf.close()
        zip_mem.seek(0)
        logger.info("done")
        zip_data = zip_mem.read()
        zip_64 = base64.b64encode(zip_data).decode('utf-8')

        logger.info(f"Mask size: {mask_b.getbuffer().nbytes}")

        progress_dict[job] = {
            "status": "results",
            "percents": results,
            "zip_file": zip_64,
            "name": f"{name}.zip"
        }

        logger.info("3")
        time.sleep(0.5)
        progress_dict[job] = progress_dict[job] = {"status": "done"}

    threading.Thread(target=background_job, args=(file_buffer, content_type, name, job)).start()
    
    return jsonify({"job_id": job})

@app.route('/progress/<job_id>')
def progress(job_id):
    def generate():
        while True:
            progress = progress_dict.get(job_id, None)
            if progress is None:
                break

            # Convert progress to a JSON-safe payload
            if isinstance(progress, dict):
                payload = progress
            elif isinstance(progress, str):
                payload = {"status": progress}
            else:
                payload = {"progress": progress}

            yield f"data: {json.dumps(payload)}\n\n"  # ✅ This is crucial

            # Break loop when job is done
            if isinstance(progress, dict) and progress.get("status") == "done":
                break

            time.sleep(0.3)

    return Response(generate(), mimetype='text/event-stream')



if __name__ == "__main__":
    app.run(port=8000, debug=True)