FROM python:slim
WORKDIR /python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./epc3928ad_exporter.py" ]