FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install --index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/ azure-search-documents==11.4.0a20230509004
RUN pip install azure-identity

# requirements.txtからパッケージをインストール
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY main.py /app/main.py
CMD ["gradio", "main.py"]
