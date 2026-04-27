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
    """Builds a premium, modern HTML string for the tool."""
    fields_html = ""
    for field in tool_data['fields']:
        if field['type'] == 'text':
            fields_html += f"""
        <div class="relative group">
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1 group-focus-within:text-blue-500 transition-colors">{field['label']}</label>
            <input type="text" id="{field['id']}" class="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none text-gray-700 placeholder-gray-300 shadow-sm" placeholder="{field['placeholder']}" required>
        </div>"""
        elif field['type'] == 'select':
            options_html = "".join([f'<option value="{opt}">{opt}</option>' for opt in field.get('options', [])])
            fields_html += f"""
        <div class="relative group">
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1 group-focus-within:text-blue-500 transition-colors">{field['label']}</label>
            <select id="{field['id']}" class="w-full px-4 py-3 bg-gray-50 border-2 border-gray-100 rounded-xl focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none text-gray-700 shadow-sm appearance-none cursor-pointer">
                {options_html}
            </select>
            <div class="absolute right-4 bottom-3.5 pointer-events-none text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
            </div>
        </div>"""

    html_template = f"""
<!-- Tailwind CSS (必須) -->
<script src="https://cdn.tailwindcss.com"></script>

<div class="tf-container max-w-2xl mx-auto p-1 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 rounded-3xl shadow-2xl mt-8">
    <div class="bg-white rounded-[1.4rem] p-8 md:p-10">
        <!-- Header -->
        <div class="mb-10 text-center">
            <div class="inline-block px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-widest rounded-full mb-4">AI Powered Solution</div>
            <h2 id="tf-title" class="text-3xl md:text-4xl font-black text-gray-900 leading-tight mb-3 italic tracking-tighter">{tool_data['title']}</h2>
            <p id="tf-description" class="text-gray-500 text-base max-w-md mx-auto">{tool_data['description']}</p>
        </div>

        <!-- Form Area -->
        <div id="tf-form-area" class="space-y-6">
            {fields_html}
            <button id="tf-generate-btn" class="w-full mt-6 bg-gray-900 hover:bg-black text-white font-bold py-4 px-6 rounded-2xl transition-all transform hover:-translate-y-1 active:scale-95 shadow-lg flex justify-center items-center overflow-hidden relative group">
                <span class="relative z-10">AIで魔法をかける</span>
                <div id="tf-loading" class="tf-loader ml-3 hidden relative z-10"></div>
                <div class="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
        </div>

        <!-- Error Area -->
        <div id="tf-error-area" class="hidden mt-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl text-sm flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
            エラーが発生しました。もう一度お試しください。
        </div>

        <!-- Result Area -->
        <div id="tf-result-area" class="hidden mt-10 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div class="flex items-center justify-between">
                <h3 class="text-xl font-bold text-gray-900 tracking-tight">生成結果</h3>
                <span class="text-xs font-medium text-green-500 bg-green-50 px-2 py-1 rounded-lg flex items-center">
                    <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse"></span> Complete
                </span>
            </div>
            <div class="relative">
                <div class="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl opacity-10 blur-sm"></div>
                <div class="relative bg-gray-50 p-6 rounded-2xl border border-gray-100 min-h-[150px]">
                    <pre id="tf-output" class="whitespace-pre-wrap text-gray-700 font-sans text-base leading-relaxed"></pre>
                </div>
            </div>
            
            <button id="tf-copy-btn" class="w-full bg-white border-2 border-gray-900 text-gray-900 hover:bg-gray-900 hover:text-white font-bold py-3 px-6 rounded-2xl transition-all flex justify-center items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" /></svg>
                <span>クリップボードにコピー</span>
            </button>

            <!-- Affiliate Section -->
            <div class="mt-12 overflow-hidden relative p-8 bg-gray-900 rounded-3xl text-white shadow-2xl">
                <div class="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
                <div class="relative z-10">
                    <h4 class="text-xl font-bold mb-3 flex items-center">
                        <span class="bg-blue-500 p-1.5 rounded-lg mr-3 shadow-lg ring-4 ring-blue-500/20">✨</span>
                        {tool_data['affiliateTitle']}
                    </h4>
                    <p class="text-gray-400 text-sm mb-6 leading-relaxed italic">{tool_data['affiliateText']}</p>
                    <a href="#affiliate" target="_blank" class="block w-full text-center bg-white text-gray-900 hover:bg-blue-50 font-black py-4 px-6 rounded-2xl transition-all shadow-xl group">
                        {tool_data['affiliateButton']} 
                        <span class="inline-block transition-transform group-hover:translate-x-1 ml-1">→</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
<style>
    .tf-loader {{ border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid white; border-radius: 50%; width: 18px; height: 18px; animation: tf-spin 0.8s linear infinite; }}
    @keyframes tf-spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
</style>
"""
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
