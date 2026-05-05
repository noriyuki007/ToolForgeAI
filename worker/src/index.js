export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Admin-Password",
    };

    // Handle CORS preflight requests
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);

    // ==========================================
    // Endpoint: /ads (Ad Management API)
    // ==========================================
    if (url.pathname === "/ads" || url.pathname === "/ads/") {
      // GET: Fetch ads from KV
      if (request.method === "GET") {
        try {
          const adsJson = await env.TF_ADS_KV.get("recommendations");
          const ads = adsJson ? JSON.parse(adsJson) : { hr: [], saas: [], finance: [], marketing: [], general: [] };
          return new Response(JSON.stringify(ads), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
        } catch (e) {
          return new Response(JSON.stringify({ error: "Failed to fetch ads" }), { status: 500, headers: corsHeaders });
        }
      }
      
      // POST: Save ads to KV (Requires Admin Password)
      if (request.method === "POST") {
        const password = request.headers.get("X-Admin-Password");
        if (!password || password !== env.ADMIN_PASSWORD) {
          return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: corsHeaders });
        }
        
        try {
          const body = await request.json();
          await env.TF_ADS_KV.put("recommendations", JSON.stringify(body));
          return new Response(JSON.stringify({ success: true }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
        } catch (e) {
          return new Response(JSON.stringify({ error: "Failed to save ads" }), { status: 500, headers: corsHeaders });
        }
      }

      return new Response("Method not allowed", { status: 405, headers: corsHeaders });
    }

    // ==========================================
    // Endpoint: / (OpenAI Wrapper)
    // ==========================================
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: corsHeaders });
    }

    try {
      const body = await request.json();
      const { userPrompt, systemPrompt } = body;

      if (!userPrompt || !systemPrompt) {
        return new Response(JSON.stringify({ error: "Missing prompts" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      // Call OpenAI API
      const openAIResponse = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${env.OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt }
          ],
          temperature: 0.7,
        })
      });

      const data = await openAIResponse.json();

      if (!openAIResponse.ok) {
        throw new Error(data.error?.message || "OpenAI API Error");
      }

      const resultText = data.choices[0].message.content;

      return new Response(JSON.stringify({ result: resultText }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  }
};
