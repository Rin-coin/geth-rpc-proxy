from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GETH_RPC_URL = "http://localhost:8545"  # GethのRPCエンドポイント

@app.route("/", methods=["POST"])
def proxy():
    # リクエストデータを取得
    data = request.get_json()

    # メソッド名の変更処理
    method_mapping = {
        "eth_getWork": "ethash_getWork",
        "eth_getHashrate": "ethash_getHashrate",
        "eth_submitWork": "ethash_submitWork",
        "eth_submitHashrate": "ethash_submitHashrate"
    }

    if data["method"] in method_mapping:
        data["method"] = method_mapping[data["method"]]

    # Gethにリクエストを転送
    response = requests.post(GETH_RPC_URL, json=data)

    # レスポンスをクライアントに返す
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
