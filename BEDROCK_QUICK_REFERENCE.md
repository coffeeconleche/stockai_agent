# AWS Bedrock Quick Reference

## 🚀 One-Line Switch

```bash
# Switch to Bedrock
AI_PROVIDER=bedrock ./deploy.sh

# Switch back to OpenAI
AI_PROVIDER=openai ./deploy.sh
```

## 📋 Prerequisites for Bedrock

1. ✅ Enable Bedrock in AWS Console
2. ✅ Request Claude model access
3. ✅ Add IAM permissions
4. ✅ Set environment variables

## ⚙️ Environment Variables

### OpenAI Version (Default)
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
GEMINI_API_KEY=your_key
```

### Bedrock Version
```bash
AI_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_TEXT=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MODEL_VISION=anthropic.claude-3-5-sonnet-20240620-v1:0
OPENAI_API_KEY=your_key  # Still needed for audio
```

## 🔑 IAM Policy for Bedrock

```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel"],
  "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"
}
```

## 💰 Cost Comparison

| Provider | Per 1K Trans | Per 10K Trans |
|----------|-------------|---------------|
| OpenAI/DeepSeek | $1.24 | $12.40 |
| Bedrock | $3.85 | $38.50 |

## ⚡ Speed Comparison

| Task | OpenAI | Bedrock |
|------|--------|---------|
| Text | 1-2s | 2-3s |
| Image | 3-4s | 4-5s |
| Audio | 5-6s | 5-6s |

## 🎯 Model IDs

### Text Processing
- **Fast & Cheap:** `anthropic.claude-3-haiku-20240307-v1:0`
- **Balanced:** `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Best:** `anthropic.claude-3-opus-20240229-v1:0`

### Image Processing
- **Recommended:** `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Best:** `anthropic.claude-3-opus-20240229-v1:0`

## 🔍 Check Current Provider

```bash
# Check logs
aws logs tail /aws/lambda/whatsapp-ai-agent --follow | grep "Using"

# Should see:
# "Using OpenAI/DeepSeek/Gemini for AI processing"
# OR
# "Using AWS Bedrock for AI processing"
```

## 🧪 Test Commands

```bash
# Test OpenAI version
export AI_PROVIDER=openai && python test.py

# Test Bedrock version
export AI_PROVIDER=bedrock && python test.py
```

## 📊 When to Use Each

### Use OpenAI/DeepSeek
- ✅ Cost is priority
- ✅ Speed matters
- ✅ Current accuracy OK
- ✅ Simple setup

### Use Bedrock
- ✅ Data privacy critical
- ✅ Compliance needed
- ✅ Want AWS-native
- ✅ Need better accuracy

## 🚨 Troubleshooting

### Bedrock: "Model access denied"
→ Request access in AWS Console → Bedrock → Model access

### Bedrock: "IAM error"
→ Add Bedrock permissions to Lambda role

### Bedrock: "Slower responses"
→ Expected, use Haiku model for speed

### Audio fails with Bedrock
→ Keep OPENAI_API_KEY for audio transcription

## 📚 Full Documentation

- **Setup Guide:** `BEDROCK_SETUP_GUIDE.md`
- **Comparison:** `AI_PROVIDER_COMPARISON.md`
- **Code:** `src/services/bedrock_service.py`

## ✨ Summary

**Two versions, one codebase:**
- Change `AI_PROVIDER` to switch
- Both fully functional
- No code changes needed
- Deploy and test! 🚀
