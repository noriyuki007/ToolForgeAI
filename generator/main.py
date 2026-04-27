import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../worker/.dev.vars')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_tool_concept():
    """Generates a niche AI tool concept and its configuration."""
    print("Generating tool concept...")
    
    prompt = """
    あなたは天才的なビジネスストラテジストであり、プログラマーです。
    高単価なアフィリエイト（転職、B2B SaaS、士業、フリーランス案件獲得など、1件1万円〜3万円の報酬）へ自然に誘導できる、
    「特定の深い悩みをワンクリックで解決する、単一機能の無料AI Webツール」のアイデアを1つ考案してください。

    以下のJSONフォーマットで厳密に出力してください。他のテキストは一切含めないでください。

    {
        "title": "ツールのタイトル（例：営業マン専用 謝罪メール作成AI）",
        "description": "ツールの説明文（2〜3行）",
        "fields": [
            {
                "id": "htmlのinput要素のID",
                "label": "フォームのラベル名",
                "placeholder": "プレースホルダー",
                "type": "text | select",
                "options": ["選択肢1", "選択肢2"] // typeがselectの場合のみ
            }
        ],
        "systemPrompt": "裏側でOpenAI APIに渡すSystem Prompt。プロフェッショナルに徹し、結果のみを出力するように指示してください。",
        "userPromptTemplate": "ユーザーの入力をどのようにプロンプトに埋め込むかのテンプレート。例: 状況: {input1}\\n相手: {input2}\\nこの条件で謝罪メールを作成してください。",
        "affiliateTitle": "アフィリエイト誘導エリアのキャッチコピー（例：これ以上クレームで悩みたくない方へ）",
        "affiliateText": "アフィリエイト誘導エリアの説明文（例：ストレスの少ないルート営業の求人を探してみませんか？）",
        "affiliateButton": "ボタンのテキスト（例：おすすめの転職エージェントを見る）"
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a helpful assistant that only outputs valid JSON."},
                  {"role": "user", "content": prompt}],
        response_format={ "type": "json_object" },
        temperature=0.8
    )

    return json.loads(response.choices[0].message.content)

def build_html(tool_data):
    """Builds the HTML string for the tool."""
    fields_html = ""
    for field in tool_data['fields']:
        if field['type'] == 'text':
            fields_html += f"""
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{field['label']}</label>
            <input type="text" id="{field['id']}" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" placeholder="{field['placeholder']}" required>
        </div>"""
        elif field['type'] == 'select':
            options_html = "".join([f'<option value="{opt}">{opt}</option>' for opt in field.get('options', [])])
            fields_html += f"""
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{field['label']}</label>
            <select id="{field['id']}" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                {options_html}
            </select>
        </div>"""

    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_data['title']} - ToolForge AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .tf-container {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        .tf-loader {{ border: 3px solid #f3f3f3; border-top: 3px solid #3b82f6; border-radius: 50%; width: 24px; height: 24px; animation: tf-spin 1s linear infinite; }}
        @keyframes tf-spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
<div class="tf-container max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100 mt-8">
    <div class="mb-6 border-b pb-4">
        <h2 id="tf-title" class="text-2xl font-bold text-gray-800">{tool_data['title']}</h2>
        <p id="tf-description" class="text-gray-600 text-sm mt-2">{tool_data['description']}</p>
    </div>

    <div id="tf-form-area" class="space-y-4">
        {fields_html}
        <button id="tf-generate-btn" class="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-md transition duration-150 flex justify-center items-center">
            <span>AIで生成する</span>
            <div id="tf-loading" class="tf-loader ml-3 hidden"></div>
        </button>
    </div>

    <div id="tf-error-area" class="hidden mt-4 p-4 bg-red-50 text-red-700 rounded-md text-sm">エラーが発生しました。もう一度お試しください。</div>

    <div id="tf-result-area" class="hidden mt-6 space-y-4">
        <h3 class="text-lg font-bold text-gray-800 border-l-4 border-blue-500 pl-2">生成結果</h3>
        <div class="bg-gray-50 p-4 rounded-md border border-gray-200">
            <pre id="tf-output" class="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed"></pre>
        </div>
        <button id="tf-copy-btn" class="w-full bg-gray-800 hover:bg-gray-900 text-white font-bold py-2 px-4 rounded-md transition duration-150">結果をコピーする</button>

        <div class="mt-8 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-lg text-center">
            <h4 class="font-bold text-gray-800 mb-2">💡 {tool_data['affiliateTitle']}</h4>
            <p class="text-sm text-gray-600 mb-4">{tool_data['affiliateText']}</p>
            <a href="#affiliate" target="_blank" class="inline-block bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-6 rounded-full shadow-md transition duration-150">
                {tool_data['affiliateButton']} ↗
            </a>
        </div>
    </div>
</div>
<script src="./script.js"></script>
</body>
</html>"""
    return html_template

def build_js(tool_data):
    """Builds the JS string for the tool."""
    
    # Create the code to extract values
    gather_values_js = ""
    for field in tool_data['fields']:
        gather_values_js += f"        const val_{field['id']} = document.getElementById('{field['id']}').value.trim();\n"
        gather_values_js += f"        if (!val_{field['id']}) {{ alert('必須項目を入力してください。'); return; }}\n"

    # Replace the {inputId} in the template with actual string interpolation
    user_prompt_js = tool_data['userPromptTemplate']
    for field in tool_data['fields']:
        user_prompt_js = user_prompt_js.replace("{" + field['id'] + "}", f"${{val_{field['id']}}}")

    js_template = f"""document.addEventListener('DOMContentLoaded', () => {{
    const generateBtn = document.getElementById('tf-generate-btn');
    const loadingIcon = document.getElementById('tf-loading');
    const btnText = generateBtn.querySelector('span');
    const resultArea = document.getElementById('tf-result-area');
    const outputArea = document.getElementById('tf-output');
    const errorArea = document.getElementById('tf-error-area');
    const copyBtn = document.getElementById('tf-copy-btn');

    // 本番環境ではCloudflare WorkerのURLに変更
    const WORKER_URL = "http://127.0.0.1:8787"; 

    generateBtn.addEventListener('click', async () => {{
        resultArea.classList.add('hidden');
        errorArea.classList.add('hidden');
        
{gather_values_js}
        
        const systemPrompt = `{tool_data['systemPrompt']}`;
        const userPrompt = `{user_prompt_js}`;

        loadingIcon.classList.remove('hidden');
        btnText.textContent = 'AIが生成中...';
        generateBtn.disabled = true;
        generateBtn.classList.add('opacity-75', 'cursor-not-allowed');

        try {{
            const response = await fetch(WORKER_URL, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ systemPrompt, userPrompt }})
            }});

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Network error');

            outputArea.textContent = data.result;
            resultArea.classList.remove('hidden');
            resultArea.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});

        }} catch (error) {{
            console.error('Generation Error:', error);
            errorArea.classList.remove('hidden');
            errorArea.textContent = `エラーが発生しました: ${{error.message}}`;
        }} finally {{
            loadingIcon.classList.add('hidden');
            btnText.textContent = 'AIで生成する';
            generateBtn.disabled = false;
            generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }}
    }});

    copyBtn.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText(outputArea.textContent);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'コピーしました！ ✓';
            copyBtn.classList.add('bg-green-600', 'hover:bg-green-700');
            copyBtn.classList.remove('bg-gray-800', 'hover:bg-gray-900');
            setTimeout(() => {{
                copyBtn.textContent = originalText;
                copyBtn.classList.add('bg-gray-800', 'hover:bg-gray-900');
                copyBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            }}, 2000);
        }} catch (err) {{ alert('コピーに失敗しました。'); }}
    }});
}});"""
    return js_template

def main():
    print("Starting ToolForge AI Generator...")
    try:
        tool_data = generate_tool_concept()
        print(f"✅ Generated Concept: {tool_data['title']}")
        
        html_content = build_html(tool_data)
        js_content = build_js(tool_data)
        
        with open("output/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        with open("output/script.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        with open("output/metadata.json", "w", encoding="utf-8") as f:
            json.dump(tool_data, f, ensure_ascii=False, indent=4)
            
        print("✅ Successfully generated tool files in 'output' directory!")

        # Send to Make.com Webhook if configured
        webhook_url = os.environ.get("MAKE_WEBHOOK_URL")
        if webhook_url:
            print(f"Sending data to Make.com webhook: {webhook_url}")
            payload = {
                "title": tool_data['title'],
                "description": tool_data['description'],
                "htmlContent": html_content,
                "jsContent": js_content,
                "affiliateTitle": tool_data['affiliateTitle']
            }
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("✅ Successfully sent to Make.com!")
            else:
                print(f"❌ Failed to send to Make.com: {response.status_code} {response.text}")
        else:
            print("⚠️ MAKE_WEBHOOK_URL not set. Skipping Make.com integration.")
        
    except Exception as e:
        print(f"❌ Error generating tool: {e}")

if __name__ == "__main__":
    main()
