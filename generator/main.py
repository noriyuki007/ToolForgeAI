import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../worker/.dev.vars')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
WORKER_URL = os.environ.get("WORKER_URL", "http://127.0.0.1:8787")

def generate_tool_concept():
    """Generates a niche AI tool concept and its configuration."""
    print("Generating tool concept...")
    
    prompt = """
    あなたは高度な専門性を持つビジネスコンサルタントであり、システムエンジニアです。
    A8.net、アクセストレード、バリューコマース、afbなどの大手ASPで取り扱われる「高単価なアフィリエイト案件（1件数千円〜数万円）」へ自然に誘導できる、
    「実務上の具体的な課題を解決し、業務効率を向上させる、単一機能の無料支援ツール」のアイデアを1つ考案してください。

    【推奨する高単価アフィリエイトジャンル（いずれかに合致させること）】
    1. 転職・キャリアアップ（ITエンジニア転職、ハイクラス転職、フリーランスエージェント）
    2. B2B SaaS・クラウドツール（会計ソフト、勤怠管理、MAツール、ビジネスチャット）
    3. 法人向け金融・インフラ（法人用クレジットカード、ビジネスローン、レンタルサーバー、独自ドメイン）
    4. スキル習得（プログラミングスクール、ビジネス英語コーチング）

    【ツール品質向上のための厳格なルール】
    1. 汎用的すぎるテーマは避け、極めてニッチで専門性の高いテーマにしてください。ただし、下記はあくまで例です。決して例と全く同じタイトルや内容を出力しないでください。独自に全く新しい斬新なアイデアを考案してください。
       (例：フリーランス向け 業務委託契約書リスク診断、B2B SaaS導入稟議書 費用対効果算出アシスタント、法人カード還元率シミュレーター、など)
    2. ツールの入力フォーム（fields）は、必ず「3つから4つ」設けてください。
    3. 入力フォームのうち、少なくとも1つは必ず「type: select」にし、専門的な選択肢を4つ以上用意してください。
    4. 「systemPrompt」には、AIの最終出力結果が「Markdown形式（マークダウンのテーブル、見出し、箇条書き）を用いて、非常に構造的かつプロフェッショナルな見た目になるよう」明確に指示を含めてください。
    5. 出力は必ず「ビジネス・プロフェッショナル」な語彙を使用し、「魔法」「驚異的」「一瞬で」などの誇張表現やカジュアルな言葉は一切排除してください。

    以下のJSONフォーマットで厳密に出力してください。他のテキストは一切含めないでください。

    {
        "title": "ツールのタイトル（例：フリーランス向け 業務委託契約書リスク診断ツール）",
        "description": "ツールの説明文（実務的なメリットを専門的かつ簡潔に記述）",
        "fields": [
            {
                "id": "htmlのinput要素のID (例: contractType)",
                "label": "フォームのラベル名",
                "placeholder": "プレースホルダー",
                "type": "text | select",
                "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"]
            }
        ],
        "systemPrompt": "OpenAI APIに渡すSystem Prompt。ビジネス実務に即した正確で論理的な回答を、【Markdownの表や見出しを用いた美しい構造】で出力するように強力に指示してください。",
        "userPromptTemplate": "ユーザーの入力をプロンプトに埋め込むテンプレート。例: 以下の条件でリスク診断をMarkdown形式で作成してください。\\n契約種別: {input1}\\n懸念事項: {input2}",
        "affiliateTitle": "アフィリエイトエリアのキャッチコピー（例：より高度な契約法務サポートをお求めの方へ）",
        "affiliateText": "アフィリエイトエリアの説明文（例：ツールの診断結果をもとに、さらに万全な体制を構築するため、フリーランス特化型の専門エージェントや法務SaaSの活用をご検討ください。）",
        "affiliateButton": "ボタンのテキスト（例：推奨サービスを確認する）"
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
<!-- Marked.js for Markdown parsing -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<!-- Google Fonts: Noto Sans JP -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">

<style>
    body {{ 
        font-family: 'Noto Sans JP', sans-serif; 
        font-style: normal !important;
    }}
    * {{
        font-style: normal !important;
    }}
    /* Custom Markdown Styles for Professional Reports */
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
        color: #111827;
        font-weight: 700;
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        line-height: 1.3;
    }}
    .markdown-body h1 {{ font-size: 1.5rem; border-bottom: 2px solid #E5E7EB; padding-bottom: 0.3em; }}
    .markdown-body h2 {{ font-size: 1.25rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 0.3em; }}
    .markdown-body h3 {{ font-size: 1.125rem; }}
    .markdown-body p {{ margin-bottom: 1em; color: #374151; line-height: 1.6; }}
    .markdown-body ul, .markdown-body ol {{
        margin-bottom: 1em;
        padding-left: 1.5em;
        color: #374151;
    }}
    .markdown-body ul {{ list-style-type: disc; }}
    .markdown-body ol {{ list-style-type: decimal; }}
    .markdown-body li {{ margin-bottom: 0.25em; }}
    .markdown-body table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1.5em;
        font-size: 0.875rem;
    }}
    .markdown-body th, .markdown-body td {{
        border: 1px solid #D1D5DB;
        padding: 0.75rem;
        text-align: left;
    }}
    .markdown-body th {{ background-color: #F3F4F6; font-weight: 700; color: #111827; }}
    .markdown-body strong {{ font-weight: 700; color: #111827; }}
    .markdown-body blockquote {{
        border-left: 4px solid #3B82F6;
        padding-left: 1em;
        color: #6B7280;
        background-color: #EFF6FF;
        padding: 0.5em 1em;
        border-radius: 0 0.5rem 0.5rem 0;
    }}
</style>

<div class="tf-container max-w-2xl mx-auto p-1 bg-gradient-to-br from-slate-200 via-blue-600 to-slate-400 rounded-3xl shadow-2xl mt-8">
    <div class="bg-white rounded-[1.4rem] p-8 md:p-10">
        <!-- Header -->
        <div class="mb-10 text-center">
            <div class="inline-block px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-widest rounded-full mb-4">ビジネス実務支援ソリューション</div>
            <h2 id="tf-title" class="text-3xl md:text-4xl font-black text-gray-900 leading-tight mb-3 tracking-tighter">{tool_data['title']}</h2>
            <p id="tf-description" class="text-gray-500 text-base max-w-md mx-auto">{tool_data['description']}</p>
        </div>

        <!-- Form Area -->
        <div id="tf-form-area" class="space-y-6">
            {fields_html}
            <button id="tf-generate-btn" class="w-full mt-6 bg-gray-900 hover:bg-black text-white font-bold py-4 px-6 rounded-2xl transition-all transform hover:-translate-y-1 active:scale-95 shadow-lg flex justify-center items-center overflow-hidden relative group">
                <span class="relative z-10">生成を実行する</span>
                <div id="tf-loading" class="tf-loader ml-3 hidden relative z-10"></div>
                <div class="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
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
                    <div id="tf-output" class="markdown-body text-base leading-relaxed"></div>
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
                        <span class="bg-blue-500 p-1.5 rounded-lg mr-3 shadow-lg ring-4 ring-blue-500/20">📊</span>
                        {tool_data['affiliateTitle']}
                    </h4>
                    <p class="text-gray-400 text-sm mb-6 leading-relaxed">{tool_data['affiliateText']}</p>
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

    js_template = f"""(() => {{
    const generateBtn = document.getElementById('tf-generate-btn');
    const loadingIcon = document.getElementById('tf-loading');
    const btnText = generateBtn.querySelector('span');
    const resultArea = document.getElementById('tf-result-area');
    const outputArea = document.getElementById('tf-output');
    const errorArea = document.getElementById('tf-error-area');
    const copyBtn = document.getElementById('tf-copy-btn');
    const WORKER_URL = "{WORKER_URL}"; 
    let lastGeneratedText = "";

    generateBtn.addEventListener('click', async () => {{
        resultArea.classList.add('hidden');
        errorArea.classList.add('hidden');
        
{gather_values_js}
        
        const systemPrompt = `{tool_data['systemPrompt']}`;
        const userPrompt = `{user_prompt_js}`;

        loadingIcon.classList.remove('hidden');
        btnText.textContent = '生成中...';
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

            lastGeneratedText = data.result;
            outputArea.innerHTML = marked.parse(data.result);
            resultArea.classList.remove('hidden');
            resultArea.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});

        }} catch (error) {{
            console.error('Generation Error:', error);
            errorArea.classList.remove('hidden');
            errorArea.textContent = `エラーが発生しました: ${{error.message}}`;
        }} finally {{
            loadingIcon.classList.add('hidden');
            btnText.textContent = 'AIで生成を実行';
            generateBtn.disabled = false;
            generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }}
    }});

    copyBtn.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText(lastGeneratedText);
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
}})();"""
    return js_template

def main():
    print("Starting ToolForge AI Generator...")
    try:
        tool_data = generate_tool_concept()
        print(f"✅ Generated Concept: {tool_data['title']}")
        
        html_content = build_html(tool_data)
        js_content = build_js(tool_data)
        
        os.makedirs("output", exist_ok=True)
        with open("output/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        with open("output/script.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        with open("output/metadata.json", "w", encoding="utf-8") as f:
            json.dump(tool_data, f, ensure_ascii=False, indent=4)
            
        print("✅ Successfully generated tool files in 'output' directory!")

        # Combine HTML and JS for WordPress embedding
        js_minified = js_content.replace('\n', ' ').replace('\r', '')
        full_content = f"{html_content}\n\n<script>{js_minified}</script>"

        # Send to Make.com Webhook if configured
        webhook_url = os.environ.get("MAKE_WEBHOOK_URL")
        if webhook_url:
            print(f"Sending data to Make.com webhook: {webhook_url}")
            payload = {
                "title": tool_data['title'],
                "description": tool_data['description'],
                "htmlContent": full_content,
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
