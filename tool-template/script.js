document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('tf-generate-btn');
    const loadingIcon = document.getElementById('tf-loading');
    const btnText = generateBtn.querySelector('span');
    const resultArea = document.getElementById('tf-result-area');
    const outputArea = document.getElementById('tf-output');
    const errorArea = document.getElementById('tf-error-area');
    const copyBtn = document.getElementById('tf-copy-btn');

    // Configuration
    // In production, this will be your actual Cloudflare Worker URL
    // e.g., "https://toolforge-api.yourusername.workers.dev"
    const WORKER_URL = "http://127.0.0.1:8787"; 

    generateBtn.addEventListener('click', async () => {
        // Hide previous results/errors
        resultArea.classList.add('hidden');
        errorArea.classList.add('hidden');
        
        // Gather inputs
        const reason = document.getElementById('tf-input-reason').value.trim();
        const role = document.getElementById('tf-input-role').value.trim();
        const gratitude = document.getElementById('tf-input-gratitude').value;

        if (!reason || !role) {
            alert('必須項目を入力してください。');
            return;
        }

        // Setup System Prompt and User Prompt specific to this tool
        const systemPrompt = `あなたはプロフェッショナルなビジネス文書作成アシスタントです。
ユーザーから提供された情報を元に、完璧なフォーマットの「退職届」と「会社に提出する退職理由の文章」を作成してください。
出力はMarkdownではなく、プレーンテキストで、そのまま印刷・コピペして使える形式にしてください。不要な前置きや後書き（「作成しました」など）は一切出力しないでください。`;

        const userPrompt = `以下の条件で退職届および退職の挨拶文を作成してください。
- 退職理由: ${reason}
- 現在の役職/職種: ${role}
- 会社への感謝の度合い: ${gratitude}

【出力構成】
1. 会社（社長宛）に提出する正式な「退職届」のフォーマット
2. 直属の上司にチャットやメールで伝えるための「退職相談・報告の文面」`;

        // Update UI state
        loadingIcon.classList.remove('hidden');
        btnText.textContent = 'AIが生成中...';
        generateBtn.disabled = true;
        generateBtn.classList.add('opacity-75', 'cursor-not-allowed');

        try {
            const response = await fetch(WORKER_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ systemPrompt, userPrompt })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Network response was not ok');
            }

            // Display result
            outputArea.textContent = data.result;
            resultArea.classList.remove('hidden');

            // Scroll to result
            resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            console.error('Generation Error:', error);
            errorArea.classList.remove('hidden');
            errorArea.textContent = `エラーが発生しました: ${error.message}`;
        } finally {
            // Restore UI state
            loadingIcon.classList.add('hidden');
            btnText.textContent = 'AIで退職届を生成する';
            generateBtn.disabled = false;
            generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    });

    copyBtn.addEventListener('click', async () => {
        const textToCopy = outputArea.textContent;
        try {
            await navigator.clipboard.writeText(textToCopy);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'コピーしました！ ✓';
            copyBtn.classList.remove('bg-gray-800', 'hover:bg-gray-900');
            copyBtn.classList.add('bg-green-600', 'hover:bg-green-700');
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.classList.add('bg-gray-800', 'hover:bg-gray-900');
                copyBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            }, 2000);
        } catch (err) {
            alert('コピーに失敗しました。');
        }
    });
});
