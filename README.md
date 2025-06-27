# 🕵️ InstaFacade - Catch Instagram Fakers Red-Handed! 🚨

**The ultimate AI detective that exposes fake content on Instagram and roasts imposters with style!** 


## 🚀 Quick Start - Get Detective Mode ON!

```bash
# 1. Clone this bad boy
git clone <repository-url>
cd InstaFacade

# 2. Install the goods
pip install -r requirements.txt

# 3. Get Instagram superpowers
git clone https://github.com/trypeggy/instagram_dm_mcp.git

# 4. Set up your secret weapons (interactive setup FTW!)
python setup_env.py
python setup_session.py

# 5. UNLEASH THE BEAST! 🎯
python src/main.py
```

## 📋 What You'll Need

- **Python 3.11+** (the newer, the better!)
- **Instagram account** with 2FA (safety first!)
- **API Keys** - Your detective toolkit:
  - 🤖 OpenAI (for that sweet GPT-4o brain)
  - 📸 ImgBB (image hosting magic)
  - 🔍 SerpAPI (reverse search wizardry)

## 🔧 Quick Config

Drop these secrets in your `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
IMGBB_API_KEY=your_imgbb_key_here
SERPAPI_KEY=your_serpapi_key_here
INSTAGRAM_USERNAME=your_insta_handle
INSTAGRAM_PASSWORD=your_super_secret_password
```

## 💥 Usage Examples - Catch 'Em All!

```bash
# 🔍 Expose that fake photo!
> Analyze image fake.jpg for authenticity

# 📸 Bust fake stories & posts
> Check @suspicious_user latest story for authenticity
> Check @faker123 latest post for fake content

# 🤖 Full auto-pilot mode - analyze AND call them out!
> Analyze fake.jpg and if fake, message @imposter about it

# 💬 Choose your roast level
> Send snarky message to @faker calling them out
> Regenerate message in SAVAGE style 🔥
> Make it professional but devastating
```

## 🏗️ Under the Hood

```
InstaFacade/
├── src/instafacade/     # 🧠 The brains
│   ├── core/           # 🎯 Agent & analyzer
│   ├── tools/          # 🛠️ LangChain arsenal
│   └── cli/            # 💬 Chat interface
├── instagram_dm_mcp/    # 📱 Instagram magic
└── setup_session.py     # 🔐 Auth wizard
```

## 🐛 Quick Fixes

| 😱 Problem | 💡 Solution |
|------------|-------------|
| 2FA Timeout | Be FAST! Approve on your phone ASAP! ⚡ |
| Missing modules | `pip install -r requirements.txt` to the rescue! |
| MCP not found | Did you clone instagram_dm_mcp? Do it! |
| API errors | Double-check that .env file! 🔍 |


## 📄 License

MIT License - Use your powers responsibly! Don't be evil 😇

---

<div align="center">

**Ready to expose some fakes? Let's GO!** 🚀

⭐ **Star us on GitHub if you love catching imposters!** ⭐

</div> 
