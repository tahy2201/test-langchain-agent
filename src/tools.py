"""LangChainエージェント用のツール関数群"""
import json
from datetime import datetime
from langchain.tools import tool
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter

# Code Interpreterセッションの管理
_CODE_INTERPRETER_CLIENT = None

def _get_code_interpreter():
    """共有Code Interpreterセッションを取得"""
    global _CODE_INTERPRETER_CLIENT
    if _CODE_INTERPRETER_CLIENT is None:
        _CODE_INTERPRETER_CLIENT = CodeInterpreter('us-west-2')
        _CODE_INTERPRETER_CLIENT.start()
    return _CODE_INTERPRETER_CLIENT


@tool
def get_weather_info(city: str) -> str:
    """指定された都市の天気情報を取得する関数
    
    Args:
        city: 天気情報を取得したい都市名（例: "Tokyo", "Osaka"）
    
    Returns:
        str: 天気情報の文字列
    """
    # モック天気データ（実際のAPIキーを使う場合はOpenWeatherMap等を使用）
    mock_weather_data = {
        "Tokyo": {"temperature": "25°C", "condition": "晴れ", "humidity": "60%"},
        "Osaka": {"temperature": "28°C", "condition": "曇り", "humidity": "70%"},
        "Kyoto": {"temperature": "24°C", "condition": "雨", "humidity": "80%"},
    }
    
    city_normalized = city.capitalize()
    
    if city_normalized in mock_weather_data:
        weather = mock_weather_data[city_normalized]
        return f"{city_normalized}の天気情報:\n" \
               f"気温: {weather['temperature']}\n" \
               f"天候: {weather['condition']}\n" \
               f"湿度: {weather['humidity']}\n" \
               f"取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        return f"申し訳ございませんが、{city}の天気情報は見つかりませんでした。"


@tool
def calculate_math_expression(expression: str) -> str:
    """数式を計算して結果を返す関数
    
    Args:
        expression: 計算したい数式（例: "2+3*4", "sqrt(16)", "sin(0.5)"）
    
    Returns:
        str: 計算結果の文字列
    """
    import math
    
    # 安全な計算のために許可する関数を定義
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("__")
    }
    allowed_names.update({
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
    })
    
    try:
        # 危険な関数呼び出しを避けるために制限付きで評価
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"計算結果: {expression} = {result}"
    except Exception as e:
        return f"計算エラー: {expression} を計算できませんでした。\n" \
               f"エラー詳細: {str(e)}\n" \
               f"使用可能な関数: sin, cos, tan, sqrt, log, exp, pi, e など"


@tool
def create_todo_item(task: str, priority: str = "medium") -> str:
    """TODOアイテムを作成してJSONファイルに保存する関数
    
    Args:
        task: タスクの内容
        priority: 優先度（"high", "medium", "low"のいずれか）
    
    Returns:
        str: 作成されたTODOアイテムの情報
    """
    import os
    
    todo_file = "todo_list.json"
    
    # TODOアイテムの作成
    todo_item = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "task": task,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "completed": False
    }
    
    # 既存のTODOリストを読み込み
    if os.path.exists(todo_file):
        try:
            with open(todo_file, "r", encoding="utf-8") as f:
                todo_list = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            todo_list = []
    else:
        todo_list = []
    
    # 新しいTODOアイテムを追加
    todo_list.append(todo_item)
    
    # ファイルに保存
    with open(todo_file, "w", encoding="utf-8") as f:
        json.dump(todo_list, f, ensure_ascii=False, indent=2)
    
    return f"TODOアイテムを作成しました:\n" \
           f"ID: {todo_item['id']}\n" \
           f"タスク: {todo_item['task']}\n" \
           f"優先度: {todo_item['priority']}\n" \
           f"作成日時: {todo_item['created_at']}"


@tool
def execute_python_code(code: str) -> str:
    """AWS Code Interpreterを使用してPythonコードを実行し、結果を返す関数
    
    Args:
        code: 実行したいPythonコード
    
    Returns:
        str: コード実行結果の文字列
    """
    try:
        
        # 共有Code Interpreterセッションを取得
        code_client = _get_code_interpreter()
        
        # コードの実行
        response = code_client.invoke("executeCode", {
            "language": "python",
            "code": code
        })
        
        # ストリーミングレスポンスから結果を抽出
        outputs = []
        errors = []
        
        for event in response["stream"]:
            if "result" not in event:
                continue
                
            result_data = event["result"]
            
            # structuredContentから出力を取得（メイン）
            if "structuredContent" in result_data:
                structured = result_data["structuredContent"]
                
                # 標準出力（print文の結果）
                stdout = structured.get("stdout", "")
                if stdout and stdout.strip():
                    outputs.append(stdout.strip())
                
                # エラー出力
                stderr = structured.get("stderr", "") 
                if stderr and stderr.strip():
                    errors.append(stderr.strip())
        
        # クリーンアップ
        # セッションは共有なので停止しない
        
        # 結果をシンプルに返す（Claudeが適切に解釈するため）
        if outputs:
            return "\n".join(outputs)
        elif errors:
            return f"エラー: \n" + "\n".join(errors)
        else:
            return "実行完了（出力なし）"
        
    except Exception as e:
        return f"Code Interpreter実行エラー: {str(e)}\n" \
               f"実行しようとしたコード:\n```python\n{code}\n```"


@tool  
def list_code_interpreter_files() -> str:
    """Code Interpreterセッション内のファイル一覧を表示する関数
    
    Returns:
        str: ファイル一覧の文字列
    """
    try:
        # 共有Code Interpreterセッションを取得
        code_client = _get_code_interpreter()
        
        # executeCodeでファイル一覧取得（より確実）
        list_code = """
import os
import datetime

# カレントディレクトリのファイル一覧を取得
files = os.listdir('.')

print("📁 Code Interpreterセッション内のファイル:")
if not files:
    print("ファイルが見つかりませんでした。")
else:
    for filename in sorted(files):
        if os.path.isfile(filename):
            file_size = os.path.getsize(filename)
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            print(f"📄 {filename} ({file_size} bytes, 更新: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
        elif os.path.isdir(filename):
            print(f"📁 {filename}/ (ディレクトリ)")
"""
        
        response = code_client.invoke("executeCode", {
            "language": "python",
            "code": list_code
        })
        
        # 実行結果を取得
        for event in response["stream"]:
            if "result" in event:
                result_data = event["result"]
                if "structuredContent" in result_data:
                    stdout = result_data["structuredContent"].get("stdout", "")
                    if stdout:
                        return stdout.strip()
        
        return "ファイル一覧の取得に失敗しました。"
            
    except Exception as e:
        return f"ファイル一覧取得エラー: {str(e)}"


@tool
def save_file_to_code_interpreter(file_path: str, content: str) -> str:
    """Code Interpreterセッションにファイルを保存する関数（executeCode使用）
    
    Args:
        file_path: 保存するファイルのパス
        content: ファイルの内容
        
    Returns:
        str: 保存結果
    """
    try:
        # 共有Code Interpreterセッションを取得
        code_client = _get_code_interpreter()
        
        # executeCodeでファイル保存（より確実）
        save_code = f"""
import os
# ファイルを保存
with open('{file_path}', 'w', encoding='utf-8') as f:
    f.write('''{content}''')

# 保存確認
if os.path.exists('{file_path}'):
    file_size = os.path.getsize('{file_path}')
    print(f"✅ ファイル '{file_path}' を保存しました（サイズ: {{file_size}} bytes）")
else:
    print(f"❌ ファイル '{file_path}' の保存に失敗しました")
"""
        
        response = code_client.invoke("executeCode", {
            "language": "python",
            "code": save_code
        })
        
        # 実行結果を取得
        for event in response["stream"]:
            if "result" in event:
                result_data = event["result"]
                if "structuredContent" in result_data:
                    stdout = result_data["structuredContent"].get("stdout", "")
                    if stdout:
                        return stdout.strip()
        
        return f"✅ ファイル '{file_path}' を保存しました"
        
    except Exception as e:
        return f"ファイル保存エラー: {str(e)}"


@tool
def download_code_interpreter_file(file_path: str) -> str:
    """Code Interpreterセッション内のファイルをダウンロードして内容を表示する関数（executeCode使用）
    
    Args:
        file_path: ダウンロードしたいファイルのパス
        
    Returns:
        str: ファイル内容またはダウンロード結果
    """
    try:
        # 共有Code Interpreterセッションを取得
        code_client = _get_code_interpreter()
        
        # executeCodeでファイル読み取り（より確実）
        read_code = f"""
import os

file_path = '{file_path}'

# ファイルの存在確認
if not os.path.exists(file_path):
    print(f"❌ ファイル '{{file_path}}' が見つかりませんでした。")
else:
    # ファイルサイズを確認
    file_size = os.path.getsize(file_path)
    print(f"📄 ファイル '{{file_path}}' の内容 ({{file_size}} bytes):")
    print("-" * 50)
    
    # テキストファイルとして読み取り試行
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 2000:
                print(content[:2000])
                print(f"\\n... (残り {{len(content) - 2000}} 文字)")
            else:
                print(content)
    except UnicodeDecodeError:
        # バイナリファイルの場合
        print("(バイナリファイルのため内容を表示できません)")
        
        # 画像ファイルの場合はbase64で出力
        if file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            import base64
            with open(file_path, 'rb') as f:
                content = f.read()
                encoded = base64.b64encode(content).decode('utf-8')
                print(f"Base64エンコード済み画像データ ({{len(encoded)}} 文字):")
                print(encoded[:100] + "..." if len(encoded) > 100 else encoded)
"""
        
        response = code_client.invoke("executeCode", {
            "language": "python",
            "code": read_code
        })
        
        # 実行結果を取得
        for event in response["stream"]:
            if "result" in event:
                result_data = event["result"]
                if "structuredContent" in result_data:
                    stdout = result_data["structuredContent"].get("stdout", "")
                    if stdout:
                        return stdout.strip()
        
        return f"❌ ファイル '{file_path}' の読み取りに失敗しました。"
        
    except Exception as e:
        return f"ファイルダウンロードエラー: {str(e)}"


def get_available_tools():
    """利用可能なツール一覧を取得"""
    return [
        get_weather_info,
        calculate_math_expression,
        create_todo_item,
        execute_python_code,
        list_code_interpreter_files,
        save_file_to_code_interpreter,
        download_code_interpreter_file
    ]
