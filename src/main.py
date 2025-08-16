"""LangChain CLI Agent - インタラクティブなAIアシスタント"""
import os
import sys
import traceback
from typing import List

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage
from tools import get_available_tools
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

# 環境変数の読み込み
load_dotenv()


def validate_aws_credentials() -> tuple[bool, str]:
    """AWS認証情報の検証"""
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not aws_access_key or not aws_secret_key:
        return False, "❌ AWS認証情報が設定されていません。\n" \
                     "環境変数 AWS_ACCESS_KEY_ID と AWS_SECRET_ACCESS_KEY を設定してください。"
    
    # 環境変数に設定（boto3が自動的に読み込む）
    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
    
    return True, ""


class LangChainCLIAgent:
    """CLIベースのLangChainエージェント"""
    
    def __init__(self):
        """エージェントの初期化"""
        self.chat_history: List = []
        self.llm = self._initialize_llm()
        
        # AWS認証情報の確認
        is_valid, error_message = validate_aws_credentials()
        if not is_valid:
            print("⚠️ AWS認証確認結果:")
            print(error_message)
            print("AWS機能（Python実行）は利用できませんが、他の機能は使用可能です。")
        
        self.agent_executor = self._create_agent()
        
        # prompt_toolkitの設定
        self.input_history = InMemoryHistory()
        self.completions = WordCompleter([
            '天気', '計算', 'TODO', 'Python', 'グラフ', 'データ', 
            'exit', 'quit', '終了'
        ])
    
    def _initialize_llm(self) -> ChatAnthropic:
        """LLMの初期化"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️ ANTHROPIC_API_KEYが設定されていません。")
            print("環境変数またはプロジェクトルートの.envファイルに設定してください。")
            sys.exit(1)
        
        return ChatAnthropic(
            model_name="claude-3-5-haiku-20241022",
            temperature=0.7,
            api_key=SecretStr(api_key),
            timeout=10,
            stop=None
        )
    
    def _create_agent(self) -> AgentExecutor:
        """エージェントの作成"""
        # ツールの取得
        tools = get_available_tools()
        
        # プロンプトテンプレートの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", """あなたは親切で知識豊富なAIアシスタントです。
            ユーザーの質問に対して、利用可能なツールを適切に使用して回答してください。
            
            利用可能なツール:
            1. get_weather_info: 天気情報の取得
            2. calculate_math_expression: 数式の計算
            3. create_todo_item: TODOアイテムの作成
            4. execute_python_code: AWS Code Interpreterを使用したPythonコード実行
            
            日本語で丁寧に回答し、必要に応じてツールを使用してください。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # エージェントの作成
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, user_input: str) -> str:
        """ユーザー入力に対する応答を生成"""
        try:
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # レスポンスの整形
            output = response["output"]
            if isinstance(output, list) and len(output) > 0:
                # リスト形式の場合、textの内容のみ抽出
                if isinstance(output[0], dict) and 'text' in output[0]:
                    output = output[0]['text']
                else:
                    output = str(output)
            elif not isinstance(output, str):
                output = str(output)
            
            # チャット履歴に追加
            self.chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=output)
            ])
            
            return output
        
        except Exception as e:
            error_msg = f"⚠️ エラーが発生しました: {str(e)}\n{traceback.format_exc()}"
            print(f"⚠️ {error_msg}")
            return error_msg
    
    def run_interactive_session(self):
        """対話型セッションの開始"""
        print("🤖 LangChain CLIエージェントにようこそ！")
        print("💡 利用可能なコマンド:")
        print("   - 天気情報: '東京の天気を教えて'")
        print("   - 計算: '2+3*4を計算して'")
        print("   - TODO作成: 'プレゼン資料作成をTODOに追加して'")
        print("   - Python実行: 'データを集計してグラフを作成して'")
        print("   - 終了: 'exit' または 'quit'")
        print("-" * 50)
        
        while True:
            try:
                # prompt_toolkitを使用した高機能入力
                try:
                    user_input = prompt(
                        "👤 あなた: ",
                        history=self.input_history,
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=self.completions,
                        complete_while_typing=True
                    ).strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\n👋 セッションを終了します...")
                    break
                except Exception as e:
                    print(f"⚠️ 入力エラー: {e}")
                    continue
                
                if user_input.lower() in ['exit', 'quit', '終了']:
                    print("👋 ありがとうございました！")
                    break
                
                if not user_input:
                    print("💬 何かご質問をどうぞ...")
                    continue
                
                print("\n🤖 エージェント:")
                response = self.chat(user_input)
                print(f"   {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 セッションを終了します...")
                break
            except Exception as e:
                print(f"⚠️ 予期しないエラー: {e}")


def main():
    """メイン関数"""
    try:
        agent = LangChainCLIAgent()
        agent.run_interactive_session()
    except Exception as e:
        print(f"❌ エージェントの初期化に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
