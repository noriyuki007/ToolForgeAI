import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv(dotenv_path="../worker/.dev.vars")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
WP_URL = os.getenv("WP_BASE_URL")
WP_USER = os.getenv("WP_USERNAME")
WP_PASS = os.getenv("WP_APP_PASSWORD")

auth = HTTPBasicAuth(WP_USER, WP_PASS)

def generate_site_content():
    print("🤖 Generating professional site content using AI...")
    prompt = """
    Create professional content for a high-end AI tool portal website named 'ToolForge AI'.
    The site provides various niche AI tools for freelancers and professionals.
    
    Output in JSON format with:
    1. 'home_title': A catchy homepage title.
    2. 'home_content': Rich HTML for the homepage including a Hero section and description. 
       Use modern Gutenberg-like blocks (HTML comments like <!-- wp:paragraph --> are not strictly necessary but clean HTML is).
    3. 'about_title': About page title.
    4. 'about_content': Professional About Us content.
    5. 'tagline': A 1-sentence catchy tagline for the site.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def create_page(title, content, slug):
    url = f"{WP_URL}/wp-json/wp/v2/pages"
    data = {
        "title": title,
        "content": content,
        "slug": slug,
        "status": "publish"
    }
    response = requests.post(url, json=data, auth=auth)
    if response.status_code == 201:
        print(f"✅ Created page: {title} ({slug})")
        return response.json()['id']
    else:
        print(f"❌ Failed to create page {slug}: {response.text}")
        return None

def clean_up_defaults():
    print("🧹 Cleaning up default WordPress content...")
    # Delete default post (ID 1)
    requests.delete(f"{WP_URL}/wp-json/wp/v2/posts/1?force=true", auth=auth)
    # Delete sample page (ID 2)
    requests.delete(f"{WP_URL}/wp-json/wp/v2/pages/2?force=true", auth=auth)
    print("✅ Cleaned up 'Hello World' and 'Sample Page'.")

def update_site_settings(tagline):
    url = f"{WP_URL}/wp-json/wp/v2/settings"
    data = {"description": tagline}
    response = requests.post(url, json=data, auth=auth)
    if response.status_code == 200:
        print(f"✅ Updated site tagline: {tagline}")
    else:
        print(f"⚠️ Could not update settings via API (Permissions?). Please update tagline manually.")

def set_front_page(page_id):
    # This often requires the 'show_on_front' and 'page_on_front' settings
    url = f"{WP_URL}/wp-json/wp/v2/settings"
    data = {
        "show_on_front": "page",
        "page_on_front": page_id
    }
    response = requests.post(url, json=data, auth=auth)
    if response.status_code == 200:
        print("✅ Successfully set the new page as the Home Page!")
    else:
        print("⚠️ Could not set Home Page via API. Please do it in Settings > Reading.")

def run_setup():
    print(f"🚀 Starting AI Site Setup for {WP_URL}...")
    
    clean_up_defaults()
    content = generate_site_content()
    
    # Create Home Page
    home_id = create_page(content['home_title'], content['home_content'], "home")
    
    # Create About Page
    create_page(content['about_title'], content['about_content'], "about")
    
    # Update Tagline
    update_site_settings(content['tagline'])
    
    # Try to set as front page
    if home_id:
        set_front_page(home_id)
    
    print("\n🎉 Site setup complete! Please check your website.")

if __name__ == "__main__":
    run_setup()
