FROM python:3.11.2

ENV PYTHONUNBUFFERED 1

# 必要なパッケージをインストール
RUN mkdir -p /root/workspace
COPY containers/requirements.txt /root/workspace/requirements.txt


WORKDIR /root/workspace


# パッケージのインストール
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt

# プロジェクトのソースコードをコンテナにコピー
COPY src/tootooroo /root/workspace/src/tootooroo



# SQLiteツールの実行権限を設定
RUN chmod +x /root/workspace/src/tootooroo/sqldiff \
    && chmod +x /root/workspace/src/tootooroo/sqlite3 \
    && chmod +x /root/workspace/src/tootooroo/sqlite3_analyzer

EXPOSE 8000


