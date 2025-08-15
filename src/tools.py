"""LangChainエージェント用のツール関数群"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from langchain.tools import tool
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter


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
def execute_python_code(code: str, description: str = "") -> str:
    """AWS Code Interpreterを使用してPythonコードを実行し、結果を返す関数
    
    Args:
        code: 実行したいPythonコード
        description: コードの説明（オプション）
    
    Returns:
        str: コード実行結果の文字列
    """
    import os
    
    try:
        # AWS認証情報の確認
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not aws_access_key or not aws_secret_key:
            return "❌ AWS認証情報が設定されていません。\n" \
                   "環境変数 AWS_ACCESS_KEY_ID と AWS_SECRET_ACCESS_KEY を設定してください。"
        
        # AWS認証情報を環境変数に設定（boto3が自動的に読み込む）
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
        
        # Code Interpreterクライアントの初期化
        code_client = CodeInterpreter('us-west-2')
        code_client.start()
        
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
        code_client.stop()
        
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


def get_available_tools():
    """利用可能なツール一覧を取得"""
    return [
        get_weather_info,
        calculate_math_expression,
        create_todo_item,
        execute_python_code,
    ]
