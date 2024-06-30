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

def get_latest_block_number():
    # eth_blockNumberメソッドを使って最新のブロック番号を取得するリクエストを作成
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    response = requests.post(GETH_RPC_URL, json=payload)
    response_data = response.json()
    # 最新のブロック番号を16進数文字列から整数に変換
    latest_block_number = int(response_data["result"], 16)
    return latest_block_number

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
            "eth_submitHashrate": "ethash_submitHashrate",
            "eth_getBlockByNumber": "eth_getBlockByNumber"  # そのままのメソッド名を保持
        }

        # リクエストデータがリスト型の場合、各要素を処理
        if isinstance(data, list):
            for item in data:
                if item["method"] in method_mapping:
                    item["method"] = method_mapping[item["method"]]
                    if item["method"] == "eth_getBlockByNumber" and item["params"] and item["params"][0] == "latest":
                        latest_block_number = get_latest_block_number()
                        item["params"][0] = hex(latest_block_number)
        else:
            if data["method"] in method_mapping:
                data["method"] = method_mapping[data["method"]]
                if data["method"] == "eth_getBlockByNumber" and data["params"] and data["params"][0] == "latest":
                    latest_block_number = get_latest_block_number()
                    data["params"][0] = hex(latest_block_number)

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
