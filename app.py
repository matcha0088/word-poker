import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_word_poker_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 単語デッキ
DECK = [
    "空", "海", "星", "風", "森", "山", "花", "時", "愛の", "ハンドクリーム",
    "夜", "朝の", "光", "闇の", "雪", "炎の", "雨", "虹", "音", "心", "鉄の",
    "おばあちゃんの", "紫外線対策", "ハゲ", "サイコパス", "100万ドルの", "夜景", "満点の",
    "０点の", "シェフの", "気まぐれサラダ", "裏", "拳", "サンド", "なのだ", "アンパン",
    "マン", "卍", "解", "なし", "東京", "さいたま", "第三者の", "懐中", "電灯", "時計",
    "魔女の", "魔女", "悪魔", "先生", "進撃の", "巨人", "テポ", "丼", "豚", "キムチ",
    "鍋", "正", "恩返し", "お金", "北の", "将軍", "朝鮮", "半島", "急がば", "回れ",
    "右", "赤色の", "最弱の", "ままの", "蟻の", "価格", "激安の", "殿堂", "入り",
    "機動戦士", "ひょうたん", "tanθ", "次郎", "sinθ", "にゃんこ", "スター", "プラチナ",
    "大戦争", "音楽", "ちょうちょ", "あぶら", "しつこい", "きもい", "風の", "谷の",
    "ナウシカ", "空飛ぶ", "家", "円盤", "投げ", "裁判", "サイパン", "アメリカの",
    "パーティー", "ピーポー", "火事", "育児", "上腕", "二頭筋", "腹筋", "崩壊",
    "ローラー", "バイキン", "マン", "うー", "囂しい", "詫び", "石", "赤みがかった",
    "カルビ", "濡れ", "乾いた", "喉の", "とんだ", "林の", "泥棒", "罪人", "ローリング",
    "'s", "肉汁餃子の", "ダンダダン", "阿鼻叫喚の", "荒らし", "NASAの", "事務", "作業",
    "蒲公英みたいな", "みたいな", "団", "陰キャ", "いにしえの", "キレイな", "という",
    "街角", "a.k.a.", "泣きっ面に", "蜂", "アホ", "サッカー", "の蜥蜴", "の生活", "リズム",
    "音読", "カード", "年老いた", "じじぃの", "おいしい", "うまい", "鳥", "月", "襟足",
    "の長い", "極めて", "共産", "赤い", "恥さらし", "この上ない", "やさい", "大昔の",
    "となりの", "トトロ", "武士", "バカの", "一つ覚え", "神様", "パパ活の", "神", "回",
    "絵", "まじ", "、", "あたらしい", "学校の", "リーダー", "らくだ", "楽天の",
    "三木谷浩史", "社長", "野田", "を溜め込んだ", "水分", "令和の", "無惨な", "良い",
    "ナイス", "極右の", "花粉症の", "チョコレート", "ケーキ", "ディスコ", "コカ",
    "コーラ", "in", "の横顔", "思想", "左寄りの", "10円", "ご飯", "パン", "卵かけ",
    "泣いた", "笑顔の", "の女", "スティーブ・ジョブズの", "パーカーをきた", "帰ってきた",
    "の生え揃った", "がどうじに", "ぐりと", "ぐら", "中古の", "地獄の", "ファッキン",
    "バイオリニスト", "ショートカット", "幕府", "江戸", "っ子", "平安", "貴族", "明日から",
    "ぎゃくに", "いちじく", "ぶどう", "仮面ライダー", "ウルトラ", "に勝った", "クワガタ虫",
    "ツツジ", "髑髏", "水晶の", "焼きかけ", "チャーシュー", "麺", "素", "人",
    "我が名は", "ふわふわと", "チャゲ＆", "が膝から崩れ落ち", "あなたの", "……なんちゃって",
    "まるで", "ドン", "番犬", "死んだので", "Im sorry", "と申します", "the", "野獣",
    "先輩", "北斗の", "剣", "ギャル", "推しの", "子", "悪魔の", "ピチピチ", "最大級の",
    "九九すら言えない", "の憂鬱", "あんかけ", "焼きそば", "チャーハン", "コーンスープ",
    "小笠原", "石造りの", "鉄製の", "ブリキの", "ダンス", "ゴースト", "ルール",
    "ライター", "違反した", "お腹を壊した", "パワーパフ", "ガールズ", "あめ", "トーク",
    "のこのこと", "マジシャン", "ローマの", "文字", "新田真剣佑の", "筋肉モリモリ",
    "握りつぶした", "マッシュルームヘアの", "転生したらスライムだった", "似の", "山田",
    "年金", "年金暮らしの", "Gの", "アク", "スタ", "メ", "で滅", "SEIKINおすすめの"
]

# ルーム・進行管理
game_state = {
    "players": {},       # {sid: {"role": "プレイヤー1" or "プレイヤー2", "phrase": ""}}
    "deck": [],
    "status": "waiting"  # "waiting", "playing", "judging", "finished"
}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    # 最大2人まで対戦プレイヤーとして登録
    if len(game_state["players"]) == 0:
        game_state["players"][sid] = {"role": "プレイヤー1", "phrase": ""}
        emit("assigned_role", {"role": "プレイヤー1"})
    elif len(game_state["players"]) == 1:
        game_state["players"][sid] = {"role": "プレイヤー2", "phrase": ""}
        emit("assigned_role", {"role": "プレイヤー2"})
        # 2人揃ったらゲーム開始
        start_game()
    else:
        # 3人目以降は観戦／ジャッジ枠
        emit("assigned_role", {"role": "観戦・ジャッジ"})
        if game_state["status"] == "judging":
            emit("judge_phase", get_phrases())

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in game_state["players"]:
        del game_state["players"][sid]
        game_state["status"] = "waiting"
        socketio.emit("reset_game", {"message": "対戦相手が退出しました。再接続を待機します。"})

def start_game():
    game_state["status"] = "playing"
    deck = DECK.copy()
    random.shuffle(deck)
    
    # 2人にそれぞれ5枚ずつ配る
    player_sids = list(game_state["players"].keys())
    hands = {
        player_sids[0]: deck[0:5],
        player_sids[1]: deck[5:10]
    }
    
    for sid in player_sids:
        game_state["players"][sid]["phrase"] = ""
        socketio.emit("game_start", {"hand": hands[sid]}, to=sid)

@socketio.on("submit_phrase")
def handle_submit(data):
    sid = request.sid
    if sid in game_state["players"]:
        game_state["players"][sid]["phrase"] = data.get("phrase", "")
        
        # 2人とも入力完了したか判定
        phrases = [p["phrase"] for p in game_state["players"].values()]
        if all(phrases):
            game_state["status"] = "judging"
            socketio.emit("judge_phase", get_phrases())

def get_phrases():
    p_data = list(game_state["players"].values())
    return {
        "p1_phrase": p_data[0]["phrase"],
        "p2_phrase": p_data[1]["phrase"]
    }

@socketio.on("send_judge")
def handle_judge(data):
    verdict = data.get("verdict")
    game_state["status"] = "finished"
    socketio.emit("game_result", {"winner": verdict, **get_phrases()})

@socketio.on("restart")
def handle_restart():
    if len(game_state["players"]) == 2:
        start_game()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
