from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からGethのRPCアドレスとプロキシサーバーのポートを取得
GETH_RPC_URL = os.getenv("GETH_RPC_URL", "http://localhost:8545")
PROXY_PORT = int(os.getenv("PROXY_PORT", 8080))

app = Flask(__name__)

@app.route("/", methods=["POST"])
def proxy():
    try:
        # リクエストデータを取得
        data = request.get_json()
        print(f"Received data: {data}")  # デバッグ用にリクエストデータを出力

        # メソッド名の変更処理
        method_mapping = {
            "eth_getWork": "ethash_getWork",
            "eth_getHashrate": "ethash_getHashrate",
            "eth_submitWork": "ethash_submitWork",
            "eth_submitHashrate": "ethash_submitHashrate"
        }

        # リクエストデータがリスト型の場合、各要素を処理
        if isinstance(data, list):
            for item in data:
                if item["method"] in method_mapping:
                    item["method"] = method_mapping[item["method"]]
        else:
            if data["method"] in method_mapping:
                data["method"] = method_mapping[data["method"]]

        # Gethにリクエストを転送
        response = requests.post(GETH_RPC_URL, json=data)
        print(f"Forwarded data: {data}")  # デバッグ用に転送データを出力

        # Gethからのレスポンスデータを取得
        response_data = response.json()
        print(f"Received from Geth: {response_data}")  # デバッグ用にGethからのレスポンスデータを出力

        # レスポンスをクライアントに返す
        return jsonify(response_data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PROXY_PORT)
