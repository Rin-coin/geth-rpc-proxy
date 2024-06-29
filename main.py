from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GETH_RPC_URL = "http://localhost:8545"  # GethのRPCエンドポイント

@app.route("/", methods=["POST"])
def proxy():
    # リクエストデータを取得
    data = request.get_json()

    # メソッドがeth_getWorkの場合、ethash_getWorkに変更
    if data["method"] == "eth_getWork":
        data["method"] = "ethash_getWork"

    # Gethにリクエストを転送
    response = requests.post(GETH_RPC_URL, json=data)

    # レスポンスをクライアントに返す
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
