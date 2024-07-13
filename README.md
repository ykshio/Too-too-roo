# Too-too-roo
`Too-too-roo`は、DjangoとBootstrap 5を使用して構築されたTwitter風のソーシャルメディアアプリです。このアプリケーションでは、ユーザーは投稿（トゥート）を作成し、他のユーザーをフォローし、投稿に「いいね」や返信をすることができます。
## 使用技術一覧
![Python](https://img.shields.io/badge/-Python_3.11.2-3776AB.svg?logo=python&style=popout)
![Django](https://img.shields.io/badge/-Django_5.0.6-092E20.svg?logo=django&style=popout)
![Javascript](https://img.shields.io/badge/-Javascript-F7DF1E.svg?logo=javascript&style=popout)
![HTML5](https://img.shields.io/badge/-HTML5-E34F26.svg?logo=html5&style=popout)
![CSS3](https://img.shields.io/badge/-CSS3-1572B6.svg?logo=css3&style=popout)
![Bootstrap](https://img.shields.io/badge/-Bootstrap_5-563D7C.svg?logo=bootstrap&style=popout)
![Docker](https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=popout)
![SQLite](https://img.shields.io/badge/-SQLite-003B57.svg?logo=sqlite&style=popout)

## 主な機能
- ユーザー認証（サインアップ・ログイン・ログアウト）
- 投稿（トゥート）の作成、表示、並び替え、絞り込み、削除
- 投稿に対する「いいね」機能
- ユーザーのフォローとフォロワー管理
- ハッシュタグによる投稿の分類と検索
- プロフィールの編集（username・表示名・プロフィール画像・自己紹介・部署）

## インストール

0. [Docker](https://www.docker.com/ja-jp/)をインストールして設定してください。
1. リポジトリをクローンします:
    ```bash
    git clone https://github.com/ykshio/Too-too-roo.git
    cd Too-too-roo
    ```
2. Dockerを使用してプロジェクトをビルドします:
    ```bash
    docker-compose build
    ```
   このコマンドは、Dockerfileを基にイメージを作成します。これにより、プロジェクトに必要な環境が整います。

3. マイグレーションを作成します:
    ```bash
    docker-compose run makemigrations
    ```

4. データベースをマイグレートします:
    ```bash
    docker-compose run migrate
    ```

5. スーパーユーザーを作成します:
    ```bash
    docker-compose run createsuperuser
    ```

6. Dockerを使用してプロジェクトを起動します:
    ```bash
    docker-compose up
    ```

これで、ブラウザから`http://localhost:8000`にアクセスすることで、アプリケーションを利用できるようになります。


## 開発経緯
- 大学のサーバープログラミング演習の課題として作成
- 自分たちだけのTwitterを作ろうということでサービス名「TooTooRoo!」とした
- 「tweet」=「toot」(警笛を鳴らす.ラッパを吹く.飲み騒ぐこと.などの意味)

## 開発期間
- 2024/6/21 ~ 
- 2024/7/12 基本的な機能は完成
- 今後は機能追加とソースコードを整理
